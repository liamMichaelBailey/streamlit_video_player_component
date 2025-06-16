import streamlit as st
from video_stream_player import video_stream_player

st.set_page_config(
    page_title="SkillCorner Report Tool",
    page_icon="skillcorner_icon.png",
    layout="wide"
)

st.logo(image='skillcorner_logo.png', size='large')
st.title('SkillCorner Video Player Component')

# Initial video dictionary
if "videos" not in st.session_state:
    st.session_state.videos = {
        'Test Clip': {
            'url': "https://cdn.pixabay.com/video/2023/04/12/158633-817153726_large.mp4",
        }
    }

# Display current videos
st.sidebar.subheader("Current Videos")

current_videos_expander = st.sidebar.expander("Current Videos")
for name, info in st.session_state.videos.items():
    with current_videos_expander:
        st.write(name)
        st.write(info['url'])
        st.video(info['url'])

# Add new video
st.sidebar.subheader("Add New Video")

with st.sidebar.form("add_video_form"):
    new_name = st.text_input("Name")
    new_url = st.text_input("Video URL")
    submitted = st.form_submit_button("Add Video")

    if submitted:
        if new_name and new_url:
            st.session_state.videos[new_name] = {
                "url": new_url,
            }
            st.success(f"Video '{new_name}' added.")
            st.rerun()
        else:
            st.error("Name and URL cannot be empty.")

# Optional: Allow deleting entries
st.sidebar.subheader("Delete Video")

with st.sidebar.container(border=True):
    delete_name = st.selectbox("Select video to delete", list(st.session_state.videos.keys()))
    if st.button("Delete Selected Video"):
        del st.session_state.videos[delete_name]
        st.success(f"Video '{delete_name}' deleted.")
        st.rerun()

st.write('Video clip dictionary:')
st.write(st.session_state.videos)
video_stream_player(video_dict=st.session_state.videos)