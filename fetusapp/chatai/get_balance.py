import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import pytz
import requests


def plot_costs_interactive_px(
    df: pd.DataFrame, title: str = "OpenAI API Daily and Cumulative Costs"
) -> px.bar:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["cumulative_cost"] = df["cost_usd"].cumsum()

    # Melt the DataFrame to long format for px.bar
    df_long = df.melt(
        id_vars="date",
        value_vars=["cost_usd", "cumulative_cost"],
        var_name="Type",
        value_name="Cost",
    )

    # Rename for nicer legend
    df_long["Type"] = df_long["Type"].map(
        {"cost_usd": "Daily Cost", "cumulative_cost": "Cumulative Cost"}
    )

    fig = px.bar(
        df_long,
        x="date",
        y="Cost",
        color="Type",
        barmode="group",
        title=title,
        labels={"date": "Date", "Cost": "Cost (USD)", "Type": "Legend"},
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["date"],
            ticktext=df["date"].dt.strftime("%Y-%m-%d"),
            tickangle=45,
        ),
        bargap=0.2,
        bargroupgap=0.1,
        template="plotly_white",
        height=600,
        width=1000,
    )
    return fig


def get_llm_cost(
    start_date: str = None, end_date: str = None, delta: int = 7
) -> pd.DataFrame:
    """
    Get OpenAI API costs for a date range.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format. If None, calculated from end_date - delta
        end_date (str): End date in 'YYYY-MM-DD' format. If None, uses today
        delta (int): Number of days to look back if start_date not provided

    Returns:
        float: Total cost in USD
    """
    api_key = os.getenv("OPENAI_ADMIN_KEY")

    headers = {"Authorization": f"Bearer {api_key}"}

    # Parse dates
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
    else:
        end_dt = datetime.now(pytz.UTC)

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
    else:
        start_dt = end_dt - timedelta(days=delta)

    # Convert to Unix timestamps
    end_time = (
        int(end_dt.timestamp() + timedelta(days=1).total_seconds()) - 1
    )  # End of the day
    start_time = int(start_dt.timestamp())

    print(
        f"Requesting data from {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')} (UTC)"
    )

    # Get ALL costs data with pagination
    all_usage_records = []
    next_page = None
    page_count = 0

    while True:
        page_count += 1
        print(f"Fetching page {page_count}...")

        url = f"https://api.openai.com/v1/organization/costs?start_time={start_time}&end_time={end_time}&bucket_width=1d"
        if next_page:
            url += f"&page={next_page}"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            for bucket in data["data"]:
                date = datetime.fromtimestamp(
                    bucket["start_time"], tz=pytz.UTC
                ).strftime("%Y-%m-%d")

                if bucket["results"]:
                    for result in bucket["results"]:
                        all_usage_records.append(
                            {
                                "date": date,
                                "cost_usd": result["amount"]["value"],
                            }
                        )
                else:
                    all_usage_records.append(
                        {
                            "date": date,
                            "cost_usd": 0.0,
                        }
                    )

            if data.get("has_more", False):
                next_page = data.get("next_page")
            else:
                print(f"  ✅ All data retrieved ({page_count} page(s))\n")
                break
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            break

    # Convert to DataFrame
    if all_usage_records:
        df = pd.DataFrame(all_usage_records)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        total_cost = df["cost_usd"].sum()

        print("=" * 60)
        print(f"Total Cost: ${total_cost:.4f} USD")
        print(f"Days with usage: {(df['cost_usd'] > 0).sum()}")
        print("=" * 60 + "\n")

        print(df)

        return df
    else:
        print("No usage records found")
        return 0.0


if __name__ == "__main__":
    pass
