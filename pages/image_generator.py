import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def image_generator_page():
    st.title("🎨 Image Generator")
    st.write("Welcome to the Image Generator feature!")
    
    # Simple image generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Generate Simple Image")
        
        # Image parameters
        width = st.slider("Width", 100, 800, 400)
        height = st.slider("Height", 100, 600, 300)
        bg_color = st.color_picker("Background Color", "#FF6B6B")
        text_content = st.text_input("Text to add", "Hello World!")
        text_color = st.color_picker("Text Color", "#FFFFFF")
        
        if st.button("Generate Image"):
            # Create a simple image
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to add text (basic font)
            try:
                # Calculate text position (center)
                text_bbox = draw.textbbox((0, 0), text_content)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                
                draw.text((x, y), text_content, fill=text_color)
            except:
                # Fallback if font issues
                draw.text((50, height//2), text_content, fill=text_color)
            
            # Display the generated image
            st.image(img, caption="Generated Image")
            
            # Provide download option
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="Download Image",
                data=byte_im,
                file_name="generated_image.png",
                mime="image/png"
            )
    
    with col2:
        st.subheader("Upload & Modify")
        
        uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Simple modifications
            if st.button("Convert to Grayscale"):
                gray_image = image.convert('L')
                st.image(gray_image, caption="Grayscale Version")
                
                # Download option for modified image
                buf = io.BytesIO()
                gray_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="Download Grayscale",
                    data=byte_im,
                    file_name="grayscale_image.png",
                    mime="image/png"
                )
    
    st.divider()
    st.info("💡 **Tip:** This is a basic image generator. You can extend it with more advanced features like filters, AI-generated images, or complex transformations!")

if __name__ == "__main__":
    image_generator_page()