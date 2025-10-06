"""
Create a transparent/blank PNG icon to remove visible app icon.
"""

import os

from PIL import Image


def create_blank_icon(size, output_path):
    """Create a completely transparent icon."""
    # Create transparent image
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img.save(output_path, "PNG")
    print(f"✓ Created blank icon: {output_path} ({size}x{size})")


# Get icons directory
script_dir = os.path.dirname(os.path.abspath(__file__))
icons_dir = os.path.join(script_dir, "fetusapp", "static", "icons")

# Create blank icons
print("Creating blank/transparent icons...")
create_blank_icon(192, os.path.join(icons_dir, "icon-192x192.png"))
create_blank_icon(512, os.path.join(icons_dir, "icon-512x512.png"))

print("\n✅ Blank icons created!")
print("The app icon will now be invisible/transparent.")
print("\nNext steps:")
print("1. Uninstall the current app")
print("2. Reinstall from http://localhost:8080")
print("3. Icon will be blank/invisible!")
