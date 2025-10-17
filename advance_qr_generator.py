import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A1, A2, A3, A4, A5
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os
import math

# Page sizes for PDF output, mapping string names to reportlab objects and dimensions in cm
PAGE_SIZES = {
    "A1": (A1, 59.4, 84.1),
    "A2": (A2, 42.0, 59.4),
    "A3": (A3, 29.7, 42.0),
    "A4": (A4, 21.0, 29.7),
    "A5": (A5, 14.8, 21.0),
}
DPI = 300  # Dots per inch for PNG conversion, a standard for printing

def cm_to_pixels(cm_value):
    """Converts centimeters to pixels based on DPI."""
    return int(cm_value * DPI / 2.54)

def get_qr_data():
    """Gets the data for QR codes from the user, handling single or range types."""
    while True:
        print("\nSelect the type of QR code to generate:")
        print("1: Single link or text")
        print("2: Range of numbers (e.g., from 001 to 100)")
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            data = input("🔗 Enter the link or text to encode: ")
            return [data]
        elif choice == '2':
            try:
                start_str = input("Enter the starting number (e.g., 00001): ")
                end_str = input("Enter the ending number (e.g., 00100): ")
                
                if not start_str.isdigit() or not end_str.isdigit():
                    print("❌ Error: Please enter valid numbers.")
                    continue

                padding = len(start_str)
                start_num = int(start_str)
                end_num = int(end_str)
                
                if start_num > end_num:
                    print("❌ Error: The starting number cannot be greater than the ending number.")
                    continue
                    
                # Generate numbers with zero-padding
                return [str(i).zfill(padding) for i in range(start_num, end_num + 1)]
            except ValueError:
                print("❌ Invalid number format. Please try again.")
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

def generate_qr_image(data, qr_width_px, qr_height_px, include_text=False):
    """Generates a single QR code image and optionally adds the data as text below it."""
    qr_img = qrcode.make(data, border=2)
    qr_img = qr_img.resize((qr_width_px, qr_height_px), Image.Resampling.LANCZOS)

    if not include_text:
        return qr_img

    # Add space for text below the QR code
    font = ImageFont.load_default(size=42)

    text_bbox = font.getbbox(data)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Create a new image with extra height for the text
    total_height = qr_height_px + text_height + 15  # 15px padding
    final_img = Image.new('RGB', (qr_width_px, total_height), 'white')
    final_img.paste(qr_img, (0, 0))

    # Draw the text centered below the QR code
    draw = ImageDraw.Draw(final_img)
    text_x = (qr_width_px - text_width) / 2
    text_y = qr_height_px + 5 # 5px padding
    draw.text((text_x, text_y), data, fill='black', font=font)

    return final_img

def main():
    """Main function to run the QR code generator workflow."""
    print("--- Advanced QR Code Generator ---")

    # 1. Get data
    qr_data_list = get_qr_data()
    if not qr_data_list:
        print("❌ No data provided. Exiting.")
        return

    # 2. Get QR dimensions in cm
    try:
        print("\nEnter QR code dimensions:")
        qr_height_cm = float(input("  -> Enter QR height in cm: "))
        qr_width_cm = float(input("  -> Enter QR width in cm: "))
    except ValueError:
        print("❌ Invalid input for dimensions. Please enter a number.")
        return

    # Convert cm to pixels for image generation
    qr_width_px = cm_to_pixels(qr_width_cm)
    qr_height_px = cm_to_pixels(qr_height_cm)

    # 3. Choose output format
    while True:
        output_format = input("\nChoose output format (PNG or PDF): ").upper()
        if output_format in ["PNG", "PDF"]:
            break
        print("❌ Invalid format. Please choose PNG or PDF.")

    # 4. Get text inclusion preference
    include_text_str = input("Include the text below the QR code? (yes/no): ").lower()
    include_text = include_text_str in ['yes', 'y']

    # Generate all QR code images in memory first
    print("\n⏳ Generating QR code images...")
    qr_images = [generate_qr_image(data, qr_width_px, qr_height_px, include_text) for data in qr_data_list]
    print("✅ All QR code images generated.")
    
    output_filename = input("\nEnter the output filename (without extension): ")

    if output_format == "PNG":
        # PNG specific settings
        try:
            total_qrs = len(qr_images)
            qrs_per_row = int(input(f"How many QR codes per row in the final PNG? (Total QRs: {total_qrs}): "))
            if qrs_per_row <= 0:
                print("❌ Must be a positive number.")
                return

            rows = (total_qrs + qrs_per_row - 1) // qrs_per_row
            
            single_qr_w, single_qr_h = qr_images[0].size
            final_width = single_qr_w * qrs_per_row
            final_height = single_qr_h * rows
            
            final_png = Image.new('RGB', (final_width, final_height), 'white')
            
            for i, qr_img in enumerate(qr_images):
                row_idx = i // qrs_per_row
                col_idx = i % qrs_per_row
                x_pos = col_idx * single_qr_w
                y_pos = row_idx * single_qr_h
                final_png.paste(qr_img, (x_pos, y_pos))

            output_path = f"{output_filename}.png"
            final_png.save(output_path)

        except ValueError:
            print("❌ Invalid number for QRs per row.")
            return

    elif output_format == "PDF":
        # --- ENHANCED PDF SETTINGS ---
        # 1. Get page size first
        while True:
            page_size_name = input(f"\nChoose PDF page size ({', '.join(PAGE_SIZES.keys())}): ").upper()
            if page_size_name in PAGE_SIZES:
                break
            print("❌ Invalid page size.")
        page_size, page_width_cm, page_height_cm = PAGE_SIZES[page_size_name]

        # 2. Get QR count preference
        qr_count_choice = input("Enter number of QRs per page, or 'max' for automatic fitting: ").lower()

        # 3. Get spacing between QRs
        try:
            row_spacing_cm = float(input("Enter space between QR rows (cm): "))
            col_spacing_cm = float(input("Enter space between QR columns (cm): "))
        except ValueError:
            print("❌ Invalid spacing value. Please enter a number.")
            return

        # Define margins and drawable area
        margin_cm = 1.0
        drawable_width_cm = page_width_cm - (2 * margin_cm)
        drawable_height_cm = page_height_cm - (2 * margin_cm)

        # 4. Calculate layout based on user choice
        if qr_count_choice == 'max':
            eff_qr_width = qr_width_cm + col_spacing_cm
            eff_qr_height = qr_height_cm + row_spacing_cm
            if eff_qr_width <= 0 or eff_qr_height <= 0:
                 print("❌ QR dimensions plus spacing must be positive.")
                 return
            qrs_per_row = int((drawable_width_cm + col_spacing_cm) // eff_qr_width)
            qrs_per_col = int((drawable_height_cm + row_spacing_cm) // eff_qr_height)
            if qrs_per_row == 0 or qrs_per_col == 0:
                print(f"❌ QR code is too large to fit on an {page_size_name} page.")
                return
            qrs_to_place_on_page = qrs_per_row * qrs_per_col
        else:
            try:
                num_qrs = int(qr_count_choice)
                if num_qrs <= 0:
                    print("❌ Number of QRs must be positive.")
                    return
                # Find a balanced grid layout (e.g., for 10, try 3x4)
                rows = int(math.sqrt(num_qrs))
                cols = math.ceil(num_qrs / rows)
                
                total_width = (cols * qr_width_cm) + (max(0, cols - 1) * col_spacing_cm)
                total_height = (rows * qr_height_cm) + (max(0, rows - 1) * row_spacing_cm)

                if total_width > drawable_width_cm or total_height > drawable_height_cm:
                    print(f"❌ A {rows}x{cols} grid for {num_qrs} QRs does not fit on {page_size_name}.")
                    print(f"  -> Needs: {total_width:.2f}x{total_height:.2f} cm | Available: {drawable_width_cm:.2f}x{drawable_height_cm:.2f} cm")
                    return
                qrs_per_row = cols
                qrs_per_col = rows
                qrs_to_place_on_page = num_qrs
            except ValueError:
                print("❌ Invalid input. Please enter a number or 'max'.")
                return

        print(f"📄 Layout: {qrs_per_row} across, {qrs_per_col} down. (Placing up to {qrs_to_place_on_page} QRs per page).")
        
        # --- PDF DRAWING LOGIC ---
        output_path = f"{output_filename}.pdf"
        c = canvas.Canvas(output_path, pagesize=page_size)
        
        grid_w = (qrs_per_row * qr_width_cm) + (max(0, qrs_per_row - 1) * col_spacing_cm)
        grid_h = (qrs_per_col * qr_height_cm) + (max(0, qrs_per_col - 1) * row_spacing_cm)
        
        # Center the entire grid on the page
        x_start = (page_width_cm - grid_w) / 2
        y_start = page_height_cm - (page_height_cm - grid_h) / 2

        current_qr_index = 0
        while current_qr_index < len(qr_images):
            qrs_on_this_page = 0
            y_pos = y_start - qr_height_cm
            
            for row in range(qrs_per_col):
                if current_qr_index >= len(qr_images) or qrs_on_this_page >= qrs_to_place_on_page: break
                x_pos = x_start
                for col in range(qrs_per_row):
                    if current_qr_index >= len(qr_images) or qrs_on_this_page >= qrs_to_place_on_page: break
                    
                    temp_img_path = f"temp_qr_{current_qr_index}.png"
                    qr_images[current_qr_index].save(temp_img_path)
                    
                    c.drawImage(temp_img_path, x_pos * cm, y_pos * cm, width=qr_width_cm*cm, height=qr_height_cm*cm)
                    
                    os.remove(temp_img_path)
                    
                    x_pos += qr_width_cm + col_spacing_cm
                    current_qr_index += 1
                    qrs_on_this_page += 1
                
                y_pos -= (qr_height_cm + row_spacing_cm)

            if current_qr_index < len(qr_images):
                c.showPage()
        
        c.save()

    full_path = os.path.abspath(output_path)
    print("\n" + "="*40)
    print(f"✅ Success! Your file has been generated.")
    print(f"  -> Saved as: {output_path}")
    print(f"  -> Location: {full_path}")
    print("="*40)

if __name__ == "__main__":
    main()
