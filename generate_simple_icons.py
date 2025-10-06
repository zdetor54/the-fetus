"""
Simple script to generate placeholder PWA icons using PIL.
Creates basic PNG icons with the app logo.

Usage:
    pip install pillow
    python generate_simple_icons.py
"""

try:
    import os

    from PIL import Image, ImageDraw, ImageFont

    def create_icon(size, output_path):
        """Create a simple icon with background color and text."""
        # Create image with pink background
        img = Image.new("RGB", (size, size), color="#EF539E")
        draw = ImageDraw.Draw(img)

        # Try to use a default font, or fall back to basic font
        try:
            # Use a larger font size proportional to icon size
            font_size = size // 4
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Draw text in center
        text = "F"

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position to center text
        x = (size - text_width) // 2
        y = (size - text_height) // 2

        # Draw white text
        draw.text((x, y), text, fill="white", font=font)

        # Draw a circle border
        circle_margin = size // 8
        draw.ellipse(
            [circle_margin, circle_margin, size - circle_margin, size - circle_margin],
            outline="white",
            width=size // 32,
        )

        # Save the image
        img.save(output_path, "PNG")
        print(f"✓ Created {output_path} ({size}x{size})")

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, "fetusapp", "static", "icons")

    # Ensure icons directory exists
    os.makedirs(icons_dir, exist_ok=True)

    # Create icons
    print("Generating PWA icons...")
    create_icon(192, os.path.join(icons_dir, "icon-192x192.png"))
    create_icon(512, os.path.join(icons_dir, "icon-512x512.png"))

    print("\n✅ All icons generated successfully!")
    print("\nNext steps:")
    print("1. (Optional) Replace these placeholder icons with custom designs")
    print("2. Run your Flask app: python app.py")
    print("3. Visit http://localhost:8080 in Chrome/Edge")
    print("4. Look for the 'Install' button in the address bar or bottom-right")
    print("5. Deploy to your server (must use HTTPS for PWA to work in production)")
    print("\n💡 For better icons, you can:")
    print("   - Use the SVG files in fetusapp/static/icons/")
    print("   - Convert them online at https://cloudconvert.com/svg-to-png")
    print("   - Or hire a designer to create professional app icons")

except ImportError as e:
    print("❌ Pillow library not installed.")
    print("\nPlease install it:")
    print("    pip install pillow")
    print(f"\nError: {e}")
except Exception as e:
    print(f"❌ Error creating icons: {e}")
    print("\nYou can create icons manually:")
    print("1. Create two PNG images: 192x192 and 512x512 pixels")
    print("2. Use a pink background (#EF539E) with white fetus logo")
    print("3. Save as icon-192x192.png and icon-512x512.png")
    print("4. Place them in: fetusapp/static/icons/")
