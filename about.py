import streamlit as st
from PIL import Image

def app():
    st.title('🗣️ About NEARVision Ⓝ')

    # Include the Font Awesome and additional CSS for animations and styling
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
        <style>
            .highlight {
                color: #2557a7; /* A color that matches your theme */
                font-weight: bold;
            }
            .about-container {
                animation: fadeInAnimation ease 3s;
                animation-iteration-count: 1;
                animation-fill-mode: forwards;
            }
            @keyframes fadeInAnimation {
                0% {
                    opacity: 0;
                }
                100% {
                    opacity: 1;
                }
            }
            .header {
            color: #ff4f8b; /* Change the color */
            font-size: 3rem; /* Change the font size */
            text-shadow: 2px 2px #ffcccb; /* Add a shadow effect */
            font-weight: bold;
            margin-bottom: 1rem;
            }
            .sub-header {
            color: #30336b; /* Change the color */
            font-size: 2rem; /* Change the font size */
            text-shadow: 1px 1px #dfe6e9; /* Add a shadow effect */
            font-weight: bold;
            margin-bottom: 1rem;
            }
            .near-symbol {
            font-size: 1.5rem; /* Change the size of the symbol */
            color: #6c5ce7; /* Change the color of the symbol */
            }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("""
       <div class="about-container" style="font-size: 1.25rem; background-color: #f0f2f6; padding: 2rem; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
        Welcome to <span class="highlight">NEARVision</span>. This platform is designed to serve as a <span class="highlight">comprehensive guide</span> and <span class="highlight">analytical tool</span> for the NEAR protocol ecosystem. NEARVision offers a deep dive into the complex workings of the NEAR blockchain, with the goal of rendering intricate data into <span class="highlight">actionable insights</span>.
        With a focus on <span class="highlight">accessibility</span> and <span class="highlight">user engagement</span>, NEARVision empowers users by providing a multifaceted view of the network's performance, transaction dynamics, and overall health. From novice enthusiasts to seasoned developers, our platform caters to a wide audience, ensuring that every user can leverage the full potential of the NEAR protocol.
        Whether you're tracking the latest market trends, analyzing smart contract interactions, or evaluating network upgrades, NEARVision equips you with the necessary tools and data. By consolidating real-time statistics, historical analysis, and predictive modeling, we aim to support informed decision-making within the NEAR community.</br>
        Embark on your journey through the NEAR ecosystem with NEARVision - where <span class="highlight">clarity meets opportunity</span>.
    </div>
    """, unsafe_allow_html=True)
    
    # Load and display an image with the 'PIL' library
    image = Image.open('Farhun.jpg')
    st.image(image, use_column_width=True)
    
    # Team member details and social icons using Font Awesome classes
    st.markdown("""
    <div style="text-align: center;">
        <h2>Mohamed Farhun M</h2>
        <p>AI Developer, Machine Learning Engineer</p>
        <p><i class="fab fa-github icon"></i> <a href="https://github.com/MohamedFarhun">Github</a></p>
        <p><i class="fab fa-linkedin-in"></i> <a href="https://www.linkedin.com/in/mohamed-farhun-m-098b68227/">LinkedIn</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer with contact information
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #f1f1f1; padding: 10px; border-radius: 5px; text-align: center;">
        <p>Contact Information:</p>
        <p>Phone: +91 93605 93132 | Email: <a href="mailto:mohamedfarhun.it20@bitsathy.ac.in">mohamedfarhun.it20@bitsathy.ac.in</a></p>
        <p>Follow on <a href="https://github.com/MohamedFarhun">Github</a> | <a href="https://www.linkedin.com/in/mohamed-farhun-m-098b68227/">LinkedIn</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()