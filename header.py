import streamlit as st

def show_header():
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0.5rem !important;
            }

            /* Fix column alignment */
            [data-testid="column"] {
                display: flex;
                align-items: center;
                justify-content: center;
            }

            div[data-testid="stButton"] button {
                background: none;
                border: none;
                font-weight: 800;
                color: white !important;
                padding: 8px 16px;
                letter-spacing: 0.5px;
                margin-top: 10px;
            }
                
            div[data-testid="stButton"] button p {
                font-size: 20px ;
            }
            div[data-testid="stButton"] button:hover {
                color: #FF4B4B !important;
                background: none;
                border: none;
            }
            hr {
                margin-top: 0rem !important;
                margin-bottom: 0rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.write("")  # small space at top

    col1, col2, col3, col4, col5, col6,col7 = st.columns([0.85, 1.05, 0.8, 0.8, 1.3, 0.7, 1])

    with col1:
        st.write("")
        st.write("")
        st.image("page_icon.png", width=90)
    with col2:
        st.write("")
        st.write("")
        if st.button("🏠  Home"):
            st.switch_page("pages/home_page.py")
    with col3:
        st.write("")
        st.write("")
        if st.button("📋  Assignments"):
            st.switch_page("pages/view_assignments.py")
    with col4:
        st.write("")
        st.write("")
        if st.button("🏆  Leaderboard"):
            st.switch_page("pages/view_leaderboard.py")
    with col5:
        st.write("")
        st.write("")
        if st.button("💬  Connect"):
            st.switch_page("pages/connect.py")
    with col6:
        st.write("")
        st.write("")
        # Default theme
        if "theme" not in st.session_state:
            st.session_state.theme = "dark"

        if st.button("☀️  Theme"):
            if st.session_state.theme == "light":
                st.session_state.theme = "dark"
            else:
                st.session_state.theme = "light"

        if st.session_state.theme == "dark":
            st.markdown(
                """
                <style>
                .stApp {
                    background-color: #121212;
                    color: #FDFDFC;
                    text-color: #0f0f0f;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        elif st.session_state.theme == "light":
            st.markdown(
                """
                <style>
                .stApp {
                    background-color: #dbd9d9;
                    color: #0f0f0f;
                }

                h1, h2, h3, h4, h5, h6, p, span, label {
                    color: #0f0f0f !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
    with col7:
        st.write("")
        st.write("")
        if st.button("👤 Profile"):
            st.switch_page("pages/my_profile.py")

    st.divider()
