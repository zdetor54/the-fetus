"""
Script to generate PWA icons from SVG files.
This creates PNG icons in the required sizes for PWA.

Usage:
    pip install pillow cairosvg
    python generate_icons.py
"""

try:
    import io
    import os

    import cairosvg
    from PIL import Image

    def svg_to_png(svg_path, png_path, size):
        """Convert SVG to PNG at specified size."""
        png_data = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
        image = Image.open(io.BytesIO(png_data))
        image.save(png_path, "PNG")
        print(f"✓ Created {png_path}")

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, "fetusapp", "static", "icons")

    # Create icons
    svg_192 = os.path.join(icons_dir, "icon-192x192.svg")
    svg_512 = os.path.join(icons_dir, "icon-512x512.svg")

    png_192 = os.path.join(icons_dir, "icon-192x192.png")
    png_512 = os.path.join(icons_dir, "icon-512x512.png")

    print("Generating PWA icons...")
    svg_to_png(svg_192, png_192, 192)
    svg_to_png(svg_512, png_512, 512)
    print("\n✅ All icons generated successfully!")
    print("\nNext steps:")
    print("1. Run your Flask app: python app.py")
    print("2. Visit http://localhost:8080 in Chrome/Edge")
    print("3. Look for the 'Install' button in the address bar")
    print("4. Deploy to your server (must use HTTPS for PWA to work)")

except ImportError as e:
    print("❌ Required libraries not installed.")
    print("\nPlease install dependencies:")
    print("    pip install pillow cairosvg")
    print("\nOr use an online converter:")
    print("    1. Go to https://cloudconvert.com/svg-to-png")
    print(
        "    2. Upload fetusapp/static/icons/icon-192x192.svg → convert to 192x192 PNG"
    )
    print(
        "    3. Upload fetusapp/static/icons/icon-512x512.svg → convert to 512x512 PNG"
    )
    print(
        "    4. Save both as icon-192x192.png and icon-512x512.png in fetusapp/static/icons/"
    )
    print(f"\nError: {e}")
