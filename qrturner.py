import qrcode
import os

# 1. Get data from user input
data = input("🔗 Enter the link or text to encode: ")

# 2. Get the desired filename from the user
filename = input("Enter the filename to save the QR code as (e.g., my_website): ")

# 3. Add the .png extension if the user didn't include it
if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
    filename += '.png'

# 4. Generate the QR code if data was entered
if data:
    try:
        img = qrcode.make(data)
        img.save(filename)
        # Get the full path to show the user where it's saved
        full_path = os.path.abspath(filename)
        print(f"\n✅ QR code successfully generated!")
        print(f"   Saved as: {filename}")
        print(f"   Location: {full_path}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
else:
    print("❌ No data was entered. Please run the script again and provide input.")