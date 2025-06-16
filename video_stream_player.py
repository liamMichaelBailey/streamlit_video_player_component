import streamlit as st
import streamlit.components.v1 as components
import json


def video_stream_player(video_dict):
    """
    A Streamlit component for playing a playlist of short video clips.
    Each video is a complete clip that plays from start to finish.

    Args:
        video_dict (dict): Dictionary of videos in the format:
            {
                'Video Title': {
                    'url': 'video_url'
                },
                ...
            }
    """
    # Convert the Python dictionary to a JSON string for JavaScript
    video_dict_json = json.dumps(video_dict)

    # Define the HTML/JS code for the component
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Video Player</title>
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
      <style>
        body {{
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          background-color: transparent;
          color: white;
          width: 100%;
        }}

        #videoContainer {{
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 100%;
          position: relative;
          max-width: 100vw;
        }}

        #videoWrapper {{
          width: 100%;
          position: relative;
          overflow: hidden;
          border-radius: 8px;
          padding-top: 56.25%; /* 16:9 Aspect Ratio */
          background-color: #000;
          transition: width 0.3s ease, padding-top 0.3s ease, transform 0.3s ease;
        }}

        #videoWrapper.playlist-open {{
          width: calc(100% - 250px);
          transform: translateX(0);
          margin-right: 0;
        }}

        #videoPlayer {{
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: block;
          object-fit: contain;
        }}

        #videoTitleOverlay {{
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          padding: 15px;
          background: linear-gradient(to bottom, rgba(0, 0, 0, 0.7), transparent);
          z-index: 12;
          font-size: 18px;
          font-weight: bold;
          color: white;
          text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }}

        #customControls {{
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
          padding: 20px 20px 10px;
          display: flex;
          align-items: center;
          opacity: 0;
          transition: opacity 0.3s ease;
          z-index: 10;
          box-sizing: border-box;
        }}

        #videoWrapper:hover #customControls,
        #customControls:hover,
        #customControls.active {{
          opacity: 1;
        }}

        .control-button {{
          background-color: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          margin-right: 15px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          border-radius: 50%;
          width: 36px;
          height: 36px;
          transition: background-color 0.2s;
          line-height: 1;
        }}

        .control-button:hover {{
          background-color: rgba(255, 255, 255, 0.3);
        }}

        .control-button .material-icons {{
          font-size: 20px;
          line-height: 1;
        }}

        .material-icons {{
          pointer-events: none;
        }}

        .remove-button .material-icons,
        .enable-button .material-icons {{
          font-size: 12px;
          line-height: 1;
        }}

        #progressContainer {{
          flex-grow: 1;
          height: 8px;
          background-color: rgba(255, 255, 255, 0.3);
          border-radius: 4px;
          margin: 0 10px;
          position: relative;
          cursor: pointer;
          overflow: visible;
        }}

        #progressBar {{
          height: 100%;
          background-color: #4CAF50;
          border-radius: 4px;
          width: 0%;
          position: relative;
          transition: width 0.1s linear;
        }}

        #progressGrabber {{
          width: 16px;
          height: 16px;
          background-color: white;
          border-radius: 50%;
          position: absolute;
          top: 50%;
          right: -8px;
          transform: translateY(-50%);
          display: none;
          box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
          z-index: 10;
        }}

        #progressContainer:hover #progressGrabber {{
          display: block;
        }}

        #progressContainer.dragging #progressGrabber {{
          display: block;
          cursor: grabbing;
        }}

        #timeDisplay {{
          color: white;
          font-size: 14px;
          min-width: 110px;
          text-align: right;
          margin-left: 5px;
        }}

        #playlistBtn {{
          position: absolute;
          top: 15px;
          right: 15px;
          background-color: rgba(0, 0, 0, 0.5);
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 8px;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          transition: background-color 0.2s, opacity 0.3s;
          z-index: 15;
          opacity: 0;
        }}

        #playlistBtn:hover {{
          background-color: rgba(76, 175, 80, 0.8);
        }}

        #videoWrapper:hover #playlistBtn {{
          opacity: 1;
        }}

        #videoWrapper.playlist-open #playlistBtn {{
          opacity: 0;
          pointer-events: none;
        }}

        #sidebar {{
          position: absolute;
          top: 0;
          right: 0;
          height: 100%;
          width: 250px;
          background-color: rgba(0, 0, 0, 0.85);
          backdrop-filter: blur(5px);
          overflow: hidden;
          z-index: 14;
          transform: translateX(100%);
          transition: transform 0.3s ease;
          display: flex;
          flex-direction: column;
          padding: 0;
          box-sizing: border-box;
          border-left: 1px solid rgba(255, 255, 255, 0.1);
          margin-left: 0;
          margin-bottom: 12px;
        }}

        #sidebar.visible {{
          transform: translateX(0);
        }}

        #sidebar.disabled {{
          pointer-events: none;
          opacity: 0.7;
        }}

        #sidebarOverlay {{
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 15;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.3s ease;
        }}

        #sidebarOverlay.visible {{
          opacity: 1;
          pointer-events: auto;
        }}

        #sidebarOverlay .message {{
          background-color: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 15px 20px;
          border-radius: 8px;
          font-size: 14px;
          text-align: center;
          max-width: 80%;
        }}

        #videoAndSidebarContainer {{
          display: flex;
          width: 100%;
          position: relative;
          justify-content: flex-start;
          align-items: stretch;
          gap: 0;
        }}

        #sidebarTitle {{
          position: sticky;
          top: 0;
          z-index: 2;
          font-size: 16px;
          font-weight: bold;
          padding: 15px;
          background-color: rgba(0, 0, 0, 0.9);
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }}

        #playlistItems {{
          padding: 15px;
          overflow-y: auto;
          flex-grow: 1;
          box-sizing: border-box;
          height: calc(100% - 51px - 100px);
        }}

        #sidebarCloseBtn {{
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          padding: 0;
          display: flex;
          align-items: center;
          justify-content: center;
        }}

        .video-item {{
          position: relative;
          display: flex;
          margin-bottom: 12px;
          width: 100%;
        }}

        .video-button {{
          padding: 10px;
          background-color: rgba(76, 175, 80, 0.2);
          color: white;
          border: none;
          cursor: pointer;
          font-size: 12px;
          border-radius: 6px;
          width: 100%;
          text-align: left;
          transition: 0.3s;
          white-space: normal;
          word-break: break-word;
        }}

        .video-button:hover {{
          background-color: rgba(76, 175, 80, 0.4);
        }}

        .active-video {{
          background-color: rgba(76, 175, 80, 0.8) !important;
          color: white !important;
          font-weight: bold;
        }}

        .disabled {{
          background-color: rgba(128, 128, 128, 0.2) !important;
          color: rgba(255, 255, 255, 0.5) !important;
          cursor: not-allowed;
        }}

        .remove-button {{
          position: absolute;
          top: -5px;
          right: -5px;
          background-color: red;
          color: white;
          border: none;
          cursor: pointer;
          padding: 5px;
          border-radius: 50%;
          font-size: 10px;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 2;
        }}

        .remove-button:hover {{
          background-color: darkred;
        }}

        .enable-button {{
          position: absolute;
          top: -5px;
          right: -5px;
          background-color: #4CAF50;
          color: white;
          border: none;
          cursor: pointer;
          padding: 5px;
          border-radius: 50%;
          font-size: 10px;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 2;
        }}

        .enable-button:hover {{
          background-color: darkgreen;
        }}

        #loadingOverlay {{
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background-color: rgba(0, 0, 0, 0.7);
          z-index: 20;
          opacity: 0;
          transition: opacity 0.3s ease;
          pointer-events: none;
        }}

        #loadingOverlay.visible {{
          opacity: 1;
          pointer-events: auto;
        }}

        .spinner {{
          width: 50px;
          height: 50px;
          border: 5px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: #4CAF50;
          animation: spin 1s ease-in-out infinite;
          margin-bottom: 15px;
        }}

        #loadingText {{
          color: white;
          font-size: 16px;
          text-align: center;
          max-width: 80%;
        }}

        @keyframes spin {{
          to {{
            transform: rotate(360deg);
          }}
        }}

        #settingsBtn {{
          background-color: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          margin-right: 15px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          border-radius: 50%;
          width: 36px;
          height: 36px;
          transition: background-color 0.2s;
          line-height: 1;
        }}

        #settingsBtn:hover {{
          background-color: rgba(255, 255, 255, 0.3);
        }}

        #settingsMenu {{
          position: absolute;
          bottom: 70px;
          left: 20px;
          background-color: rgba(0, 0, 0, 0.75);
          backdrop-filter: blur(5px);
          border-radius: 8px;
          padding: 15px;
          display: none;
          flex-direction: column;
          gap: 12px;
          z-index: 15;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
          transition: opacity 0.3s, transform 0.3s;
          opacity: 0;
          transform: translateY(10px);
          min-width: 220px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        #settingsMenu.visible {{
          display: flex;
          opacity: 1;
          transform: translateY(0);
        }}

        .menu-item {{
          display: flex;
          align-items: center;
          margin-bottom: 10px;
        }}

        .menu-item:last-child {{
          margin-bottom: 0;
        }}

        .menu-label {{
          color: rgba(255, 255, 255, 0.9);
          font-size: 14px;
          margin-right: 10px;
          min-width: 60px;
          font-weight: 500;
        }}

        .menu-controls {{
          display: flex;
          align-items: center;
          gap: 5px;
        }}

        .menu-button {{
          background-color: rgba(255, 255, 255, 0.15);
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: background-color 0.2s, transform 0.1s;
        }}

        .menu-button:hover {{
          background-color: rgba(255, 255, 255, 0.25);
          transform: translateY(-1px);
        }}

        .menu-button:active {{
          transform: translateY(0);
        }}

        .menu-button.active {{
          background-color: #4CAF50;
        }}

        #notification {{
          position: absolute;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          background-color: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 10px 20px;
          border-radius: 4px;
          font-size: 14px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
          z-index: 30;
          opacity: 0;
          transition: opacity 0.3s;
          pointer-events: none;
          text-align: center;
        }}

        #notification.visible {{
          opacity: 1;
        }}

        #downloadsBtn {{
          background-color: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          margin-right: 15px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          border-radius: 50%;
          width: 36px;
          height: 36px;
          transition: background-color 0.2s;
          line-height: 1;
        }}

        #downloadsBtn:hover {{
          background-color: rgba(255, 255, 255, 0.3);
        }}

        #downloadsMenu {{
          position: absolute;
          bottom: 70px;
          left: 70px;
          background-color: rgba(0, 0, 0, 0.75);
          backdrop-filter: blur(5px);
          border-radius: 8px;
          padding: 15px;
          display: none;
          flex-direction: column;
          gap: 12px;
          z-index: 15;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
          transition: opacity 0.3s, transform 0.3s;
          opacity: 0;
          transform: translateY(10px);
          min-width: 220px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        #downloadsMenu.visible {{
          display: flex;
          opacity: 1;
          transform: translateY(0);
        }}

        #playlistItems::-webkit-scrollbar {{
          width: 8px;
        }}

        #playlistItems::-webkit-scrollbar-track {{
          background: rgba(0, 0, 0, 0.2);
          border-radius: 4px;
          margin: 2px;
        }}

        #playlistItems::-webkit-scrollbar-thumb {{
          background: rgba(255, 255, 255, 0.3);
          border-radius: 4px;
        }}

        #playlistItems::-webkit-scrollbar-thumb:hover {{
          background: rgba(255, 255, 255, 0.5);
        }}

        #playlistSettings {{
          padding: 15px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          background-color: rgba(0, 0, 0, 0.7);
          position: sticky;
          bottom: 0;
          z-index: 2;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }}

        .playlist-setting-button {{
          background-color: rgba(255, 255, 255, 0.15);
          color: white;
          border: none;
          padding: 8px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
          width: 100%;
          transition: background-color 0.2s, transform 0.1s;
          font-weight: 500;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }}

        .playlist-setting-button:hover {{
          background-color: rgba(255, 255, 255, 0.25);
          transform: translateY(-1px);
        }}

        .playlist-setting-button:active {{
          transform: translateY(0);
        }}

        .playlist-setting-button .material-icons {{
          font-size: 16px;
        }}

        #downloadPlaylistBtn {{
          background-color: rgba(76, 175, 80, 0.4);
          color: white;
          border: none;
          padding: 8px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
          width: 100%;
          transition: background-color 0.2s, transform 0.1s;
          font-weight: 500;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          margin-top: 5px;
        }}

        #downloadPlaylistBtn:hover {{
          background-color: rgba(76, 175, 80, 0.6);
          transform: translateY(-1px);
        }}

        #downloadPlaylistBtn:active {{
          transform: translateY(0);
        }}

        #downloadPlaylistBtn:disabled {{
          background-color: rgba(128, 128, 128, 0.2);
          color: rgba(255, 255, 255, 0.5);
          cursor: not-allowed;
          transform: none;
        }}

        .expander {{
          width: 100%;
          margin-top: 10px;
        }}

        .expander-header {{
          background-color: rgba(255, 255, 255, 0.1);
          color: white;
          border: none;
          padding: 8px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
          width: 100%;
          text-align: left;
          transition: background-color 0.2s;
          font-weight: 500;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }}

        .expander-header:hover {{
          background-color: rgba(255, 255, 255, 0.2);
        }}

        .expander-content {{
          display: none;
          padding-top: 10px;
          flex-direction: column;
          gap: 10px;
        }}

        .expander-content.expanded {{
          display: flex;
        }}

        .expander-icon {{
          transition: transform 0.3s;
        }}

        .expander-icon.expanded {{
          transform: rotate(180deg);
        }}

        @media (max-width: 768px) {{
          #videoWrapper.playlist-open {{
            width: 100%;
          }}

          #sidebar.visible {{
            position: relative;
            width: 100%;
            margin-top: 10px;
            height: auto;
            min-height: 300px;
          }}

          #videoWrapper.playlist-open + #sidebar.visible {{
            position: relative;
            width: 100%;
          }}

          #playlistItems {{
            height: auto;
            max-height: 300px;
          }}
        }}

        iframe {{
          width: 100% !important;
        }}
      </style>
    </head>
    <body>
      <div id="videoContainer">
        <div id="videoAndSidebarContainer">
          <div id="videoWrapper">
            <video id="videoPlayer" preload="auto" muted playsinline autoplay>
              Your browser does not support the video tag.
            </video>

            <div id="videoTitleOverlay"></div>

            <button id="playlistBtn" class="control-button">
              <i class="material-icons">playlist_play</i>
            </button>

            <div id="loadingOverlay">
              <div class="spinner"></div>
              <div id="loadingText">Loading...</div>
            </div>

            <div id="notification">Notification message</div>

            <div id="settingsMenu">
              <div class="menu-item">
                <div class="menu-label">Audio:</div>
                <div class="menu-controls">
                  <button id="muteBtn" class="menu-button">Mute</button>
                </div>
              </div>
            </div>

            <div id="downloadsMenu">
              <div class="menu-item">
                <div class="menu-label">Video:</div>
                <div class="menu-controls">
                  <button id="downloadClipBtn" class="menu-button">Download Clip</button>
                </div>
              </div>
            </div>

            <div id="customControls">
              <button id="playPauseBtn" class="control-button"><i class="material-icons">pause</i></button>
              <button id="settingsBtn" class="control-button"><i class="material-icons">settings</i></button>
              <button id="downloadsBtn" class="control-button"><i class="material-icons">download</i></button>

              <div id="progressContainer">
                <div id="progressBar">
                  <div id="progressGrabber"></div>
                </div>
              </div>
              <div id="timeDisplay">0:00 / 0:00</div>
            </div>
          </div>

          <div id="sidebar">
            <div id="sidebarOverlay"></div>
            <div id="sidebarTitle">
              <span>Video Playlist</span>
              <button id="sidebarCloseBtn">
                <i class="material-icons">close</i>
              </button>
            </div>
            <div id="playlistItems"></div>
            <div id="playlistSettings">
              <button id="downloadPlaylistBtn" class="playlist-setting-button">
                <i class="material-icons">archive</i> Download as ZIP
              </button>

              <div class="expander">
                <button id="playlistSettingsExpander" class="expander-header">
                  <span>Playlist Settings</span>
                  <i class="material-icons expander-icon">expand_more</i>
                </button>
                <div id="playlistSettingsContent" class="expander-content">
                  <button id="enableAllClipsBtn" class="playlist-setting-button">
                    <i class="material-icons">check_circle</i> Enable All Clips
                  </button>
                  <button id="disableAllClipsBtn" class="playlist-setting-button">
                    <i class="material-icons">cancel</i> Disable All Clips
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div id="preloadContainer" style="display:none;"></div>
      </div>

      <script>
        // Parse the video dictionary from Python
        const videoDict = {video_dict_json};
        const videoKeys = Object.keys(videoDict);
        const disabledVideos = new Set();
        let isPlaying = false;
        let isDragging = false;
        let isMuted = true;
        let controlsTimeout = null;
        let notificationTimeout = null;
        let currentVideoKey = null;
        let isSettingsOpen = false;
        let isDownloading = false;
        let isDownloadsOpen = false;
        let isPlaylistOpen = false;
        const downloadsMenu = document.getElementById('downloadsMenu');
        const downloadClipBtn = document.getElementById('downloadClipBtn');
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        const playlistBtn = document.getElementById('playlistBtn');
        const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
        const videoTitleOverlay = document.getElementById('videoTitleOverlay');
        const playlistItems = document.getElementById('playlistItems');
        const downloadPlaylistBtn = document.getElementById('downloadPlaylistBtn');
        const playlistSettingsExpander = document.getElementById('playlistSettingsExpander');
        const playlistSettingsContent = document.getElementById('playlistSettingsContent');

        // DOM elements
        const videoPlayer = document.getElementById('videoPlayer');
        const videoWrapper = document.getElementById('videoWrapper');
        const playPauseBtn = document.getElementById('playPauseBtn');
        const muteBtn = document.getElementById('muteBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const progressGrabber = document.getElementById('progressGrabber');
        const timeDisplay = document.getElementById('timeDisplay');
        const customControls = document.getElementById('customControls');
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        const settingsBtn = document.getElementById('settingsBtn');
        const settingsMenu = document.getElementById('settingsMenu');
        const notification = document.getElementById('notification');
        const downloadBtn = document.getElementById('downloadsBtn');
        const enableAllClipsBtn = document.getElementById('enableAllClipsBtn');
        const disableAllClipsBtn = document.getElementById('disableAllClipsBtn');

        // Function to disable/enable sidebar
        function setSidebarDisabled(disabled) {{
          if (disabled) {{
            sidebar.classList.add('disabled');
            sidebarOverlay.classList.add('visible');
          }} else {{
            sidebar.classList.remove('disabled');
            sidebarOverlay.classList.remove('visible');
          }}
        }}

        // Toggle playlist sidebar
        function togglePlaylist() {{
          isPlaylistOpen = !isPlaylistOpen;

          if (isPlaylistOpen) {{
            sidebar.classList.add('visible');
            videoWrapper.classList.add('playlist-open');
          }} else {{
            sidebar.classList.remove('visible');
            videoWrapper.classList.remove('playlist-open');
          }}
        }}

        // Toggle playlist settings expander
        function togglePlaylistSettingsExpander() {{
          const expanderIcon = playlistSettingsExpander.querySelector('.expander-icon');
          if (playlistSettingsContent.classList.contains('expanded')) {{
            playlistSettingsContent.classList.remove('expanded');
            expanderIcon.classList.remove('expanded');
          }} else {{
            playlistSettingsContent.classList.add('expanded');
            expanderIcon.classList.add('expanded');
          }}
        }}

        // Close playlist sidebar
        function closePlaylist() {{
          isPlaylistOpen = false;
          sidebar.classList.remove('visible');
          videoWrapper.classList.remove('playlist-open');
        }}

        // Show unified notification
        function showUnifiedNotification(message, options = {{}}) {{
          const {{ 
            duration = 3000,
            showSpinner = false,
            spinnerText = message,
            showToast = true
          }} = options;

          if (showToast) {{
            if (notificationTimeout) {{
              clearTimeout(notificationTimeout);
            }}

            notification.textContent = message;
            notification.classList.add('visible');

            notificationTimeout = setTimeout(() => {{
              notification.classList.remove('visible');
            }}, duration);
          }}

          if (showSpinner) {{
            loadingText.textContent = spinnerText;
            loadingOverlay.classList.add('visible');

            if (options.spinnerDuration) {{
              setTimeout(() => {{
                loadingOverlay.classList.remove('visible');
              }}, options.spinnerDuration);
            }}
          }} else if (options.hideSpinner) {{
            loadingOverlay.classList.remove('visible');
          }}
        }}

        // Format time in MM:SS format
        function formatTime(seconds) {{
          const minutes = Math.floor(seconds / 60);
          const secs = Math.floor(seconds % 60);
          return `${{minutes}}:${{secs.toString().padStart(2, '0')}}`;
        }}

        // Get active (not disabled) videos
        function getActiveVideos() {{
          return videoKeys.filter(k => !disabledVideos.has(k));
        }}

        // Update progress bar and time display
        function updateProgressBar() {{
          if (!currentVideoKey || !videoPlayer.duration) return;

          const currentTime = videoPlayer.currentTime;
          const duration = videoPlayer.duration;
          const progress = (currentTime / duration) * 100;

          progressBar.style.width = `${{progress}}%`;

          const formattedCurrentTime = formatTime(currentTime);
          const formattedDuration = formatTime(duration);
          timeDisplay.textContent = `${{formattedCurrentTime}} / ${{formattedDuration}}`;
        }}

        // Set video time based on progress bar position
        function setVideoTimeFromPosition(posX) {{
          if (!videoPlayer.duration) return;

          const rect = progressContainer.getBoundingClientRect();
          const clickPos = Math.max(0, Math.min(1, (posX - rect.left) / rect.width));
          const newTime = videoPlayer.duration * clickPos;

          videoPlayer.currentTime = newTime;
          updateProgressBar();
        }}

        // Toggle settings menu
        function toggleSettingsMenu() {{
          isSettingsOpen = !isSettingsOpen;
          if (isSettingsOpen) {{
            settingsMenu.classList.add('visible');
          }} else {{
            settingsMenu.classList.remove('visible');
          }}
        }}

        // Toggle downloads menu
        function toggleDownloadsMenu() {{
          isDownloadsOpen = !isDownloadsOpen;
          if (isDownloadsOpen) {{
            downloadsMenu.classList.add('visible');
            if (isSettingsOpen) {{
              isSettingsOpen = false;
              settingsMenu.classList.remove('visible');
            }}
          }} else {{
            downloadsMenu.classList.remove('visible');
          }}
        }}

        // Load a specific video by key
        function loadVideo(videoKey) {{
          if (!videoKey || disabledVideos.has(videoKey)) return;

          currentVideoKey = videoKey;
          const videoData = videoDict[videoKey];

          showUnifiedNotification("Loading video...", {{ 
            showSpinner: true, 
            showToast: false 
          }});

          videoPlayer.src = videoData.url;
          videoTitleOverlay.textContent = videoKey;

          videoPlayer.onloadedmetadata = () => {{
            updateProgressBar();
            // Auto play the video
            videoPlayer.play().then(() => {{
              isPlaying = true;
              playPauseBtn.innerHTML = '<i class="material-icons">pause</i>';
            }}).catch(err => console.error("Error auto-playing video:", err));
          }};

          updateSidebar();
          updateMuteButtonText();
        }}

        // Load next video in playlist
        function loadNextVideo() {{
          const activeVideos = getActiveVideos();
          if (activeVideos.length === 0) return;

          const currentIndex = activeVideos.indexOf(currentVideoKey);

          if (currentIndex < activeVideos.length - 1) {{
            loadVideo(activeVideos[currentIndex + 1]);
          }} else {{
            videoPlayer.pause();
            playPauseBtn.innerHTML = '<i class="material-icons">play_arrow</i>';
            isPlaying = false;
            showUnifiedNotification("End of playlist reached");
          }}
        }}

        // Update sidebar UI
        function updateSidebar() {{
          playlistItems.innerHTML = '';

          videoKeys.forEach((videoKey) => {{
            const wrapper = document.createElement("div");
            wrapper.classList.add("video-item");

            const button = document.createElement("button");
            button.classList.add("video-button");
            button.textContent = videoKey;
            button.onclick = () => {{
              if (!disabledVideos.has(videoKey)) {{
                loadVideo(videoKey);
              }}
            }};

            if (disabledVideos.has(videoKey)) {{
              button.classList.add("disabled");
            }}

            if (videoKey === currentVideoKey) {{
              button.classList.add("active-video");
            }}

            const toggleButton = document.createElement("button");

            if (disabledVideos.has(videoKey)) {{
              toggleButton.classList.add("enable-button");
              toggleButton.innerHTML = '<i class="material-icons" style="font-size: 12px;">check</i>';
              toggleButton.onclick = (event) => {{
                event.stopPropagation();
                enableVideo(videoKey);
              }};
            }} else {{
              toggleButton.classList.add("remove-button");
              toggleButton.innerHTML = '<i class="material-icons" style="font-size: 12px;">close</i>';
              toggleButton.onclick = (event) => {{
                event.stopPropagation();
                disableVideo(videoKey);
              }};
            }}

            wrapper.appendChild(button);
            wrapper.appendChild(toggleButton);
            playlistItems.appendChild(wrapper);
          }});

          updateDownloadPlaylistButton();
        }}

        // Update download playlist button state
        function updateDownloadPlaylistButton() {{
          const activeVideos = getActiveVideos();
          if (activeVideos.length < 1 || isDownloading) {{
            downloadPlaylistBtn.disabled = true;
            downloadPlaylistBtn.textContent = activeVideos.length < 1 ? 
              "No Active Clips" : "Creating ZIP...";
          }} else {{
            downloadPlaylistBtn.disabled = false;
            downloadPlaylistBtn.innerHTML = '<i class="material-icons">archive</i> Download as ZIP';
          }}
        }}

        // Disable a video
        function disableVideo(videoKey) {{
          disabledVideos.add(videoKey);

          if (videoKey === currentVideoKey) {{
            loadNextVideo();
          }}

          updateSidebar();
        }}

        // Enable a video
        function enableVideo(videoKey) {{
          disabledVideos.delete(videoKey);
          updateSidebar();
        }}

        // Toggle play/pause
        function togglePlayPause() {{
          if (videoPlayer.paused) {{
            videoPlayer.play();
            playPauseBtn.innerHTML = '<i class="material-icons">pause</i>';
            isPlaying = true;
          }} else {{
            videoPlayer.pause();
            playPauseBtn.innerHTML = '<i class="material-icons">play_arrow</i>';
            isPlaying = false;
          }}
        }}

        // Update mute button text
        function updateMuteButtonText() {{
          muteBtn.textContent = videoPlayer.muted ? "Unmute" : "Mute";
        }}

        // Toggle mute/unmute
        function toggleMute() {{
          videoPlayer.muted = !videoPlayer.muted;
          isMuted = videoPlayer.muted;
          updateMuteButtonText();
        }}

        // Show controls temporarily
        function showControlsTemporarily() {{
          customControls.classList.add('active');

          if (controlsTimeout) {{
            clearTimeout(controlsTimeout);
          }}

          controlsTimeout = setTimeout(() => {{
            if (!videoWrapper.matches(':hover') && !isDragging && !isSettingsOpen && !isDownloadsOpen) {{
              customControls.classList.remove('active');
            }}
          }}, 3000);
        }}

        // Video event listeners
        videoPlayer.addEventListener('timeupdate', () => {{
          if (!isDragging) {{
            updateProgressBar();
          }}
        }});

        videoPlayer.addEventListener('ended', () => {{
          loadNextVideo();
        }});

        // Download current clip (force download using blob)
        async function downloadCurrentClip() {{
          if (!currentVideoKey || !videoDict[currentVideoKey] || isDownloading) return;

          isDownloading = true;
          setSidebarDisabled(true);

          const videoData = videoDict[currentVideoKey];
          const videoUrl = videoData.url;
          const filename = currentVideoKey.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.mp4';

          showUnifiedNotification("Starting download...", {{
            showSpinner: true,
            spinnerText: "Preparing download...",
            duration: 3000
          }});

          try {{
            // Fetch the video as a blob
            const response = await fetch(videoUrl);
            if (!response.ok) {{
              throw new Error('Failed to fetch video: ' + response.status);
            }}

            const blob = await response.blob();

            // Create object URL and download link
            const blobUrl = URL.createObjectURL(blob);
            const downloadLink = document.createElement('a');
            downloadLink.href = blobUrl;
            downloadLink.download = filename;
            downloadLink.style.display = 'none';

            document.body.appendChild(downloadLink);
            downloadLink.click();

            // Clean up
            setTimeout(() => {{
              document.body.removeChild(downloadLink);
              URL.revokeObjectURL(blobUrl);
              showUnifiedNotification("Download completed! Check your downloads folder.", {{
                hideSpinner: true
              }});
              isDownloading = false;
              setSidebarDisabled(false);
            }}, 1000);

          }} catch (error) {{
            console.error('Error downloading clip:', error);
            showUnifiedNotification('Error: Failed to download clip. ' + (error.message || 'Please try again.'), {{
              hideSpinner: true
            }});
            isDownloading = false;
            setSidebarDisabled(false);
          }}
        }}

        // Download all active clips as ZIP
        async function downloadAllClips() {{
          const activeVideos = getActiveVideos();
          if (activeVideos.length < 1 || isDownloading) return;

          isDownloading = true;
          updateDownloadPlaylistButton();
          setSidebarDisabled(true);

          showUnifiedNotification("Creating ZIP file...", {{
            showSpinner: true,
            spinnerText: "Preparing ZIP download...",
            duration: 5000
          }});

          try {{
            // Create a new JSZip instance
            const zip = new JSZip();

            // Download each active video and add to zip
            for (let i = 0; i < activeVideos.length; i++) {{
              const videoKey = activeVideos[i];
              const videoData = videoDict[videoKey];
              const filename = videoKey.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.mp4';

              showUnifiedNotification('Adding ' + (i + 1) + ' of ' + activeVideos.length + ' to ZIP...', {{
                showSpinner: true,
                spinnerText: 'Processing ' + videoKey + '...',
                showToast: false
              }});

              try {{
                // Fetch the video as a blob
                const response = await fetch(videoData.url);
                if (!response.ok) {{
                  console.warn('Failed to fetch ' + videoKey + ': ' + response.status);
                  continue;
                }}

                const blob = await response.blob();

                // Add the blob to the zip file
                zip.file(filename, blob);

              }} catch (error) {{
                console.warn('Failed to add ' + videoKey + ' to ZIP:', error);
                continue;
              }}
            }}

            showUnifiedNotification("Generating ZIP file...", {{
              showSpinner: true,
              spinnerText: "Finalizing download...",
              showToast: false
            }});

            // Generate the zip file
            const zipBlob = await zip.generateAsync({{type: "blob"}});

            // Create download link for the zip file
            const zipUrl = URL.createObjectURL(zipBlob);
            const downloadLink = document.createElement('a');
            downloadLink.href = zipUrl;
            downloadLink.download = 'video_clips.zip';
            downloadLink.style.display = 'none';

            document.body.appendChild(downloadLink);
            downloadLink.click();

            // Clean up
            setTimeout(() => {{
              document.body.removeChild(downloadLink);
              URL.revokeObjectURL(zipUrl);
            }}, 1000);

            showUnifiedNotification('ZIP file created! Downloaded ' + activeVideos.length + ' clips as video_clips.zip', {{
              hideSpinner: true,
              duration: 5000
            }});

          }} catch (error) {{
            console.error('Error creating ZIP file:', error);
            showUnifiedNotification('Error: Failed to create ZIP file. ' + (error.message || 'Please try again.'), {{
              hideSpinner: true
            }});
          }} finally {{
            isDownloading = false;
            updateDownloadPlaylistButton();
            setSidebarDisabled(false);
          }}
        }}

        // Enable all clips in the playlist
        function enableAllClips() {{
          disabledVideos.clear();
          updateSidebar();
          showUnifiedNotification("All clips enabled");
        }}

        // Disable all clips in the playlist
        function disableAllClips() {{
          videoKeys.forEach(key => {{
            disabledVideos.add(key);
          }});

          updateSidebar();
          showUnifiedNotification("All clips disabled");

          videoPlayer.pause();
          playPauseBtn.innerHTML = '<i class="material-icons">play_arrow</i>';
          isPlaying = false;
        }}

        // Event listeners
        playPauseBtn.addEventListener('click', togglePlayPause);
        settingsBtn.addEventListener('click', toggleSettingsMenu);
        downloadBtn.addEventListener('click', toggleDownloadsMenu);
        playlistBtn.addEventListener('click', togglePlaylist);
        sidebarCloseBtn.addEventListener('click', closePlaylist);
        muteBtn.addEventListener('click', toggleMute);
        videoPlayer.addEventListener('click', togglePlayPause);

        // Progress bar event listeners
        progressContainer.addEventListener('click', (e) => {{
          if (isDragging) return;
          setVideoTimeFromPosition(e.clientX);
        }});

        progressContainer.addEventListener('mousedown', (e) => {{
          isDragging = true;
          progressContainer.classList.add('dragging');
          setVideoTimeFromPosition(e.clientX);

          const wasPlaying = !videoPlayer.paused;
          if (wasPlaying) {{
            videoPlayer.pause();
          }}

          function handleMouseMove(e) {{
            if (isDragging) {{
              setVideoTimeFromPosition(e.clientX);
              e.preventDefault();
            }}
          }}

          function handleMouseUp(e) {{
            if (isDragging) {{
              isDragging = false;
              progressContainer.classList.remove('dragging');
              setVideoTimeFromPosition(e.clientX);

              if (wasPlaying) {{
                videoPlayer.play();
              }}

              document.removeEventListener('mousemove', handleMouseMove);
              document.removeEventListener('mouseup', handleMouseUp);
            }}
          }}

          document.addEventListener('mousemove', handleMouseMove);
          document.addEventListener('mouseup', handleMouseUp);
        }});

        // Close menus when clicking outside
        document.addEventListener('click', (e) => {{
          if (isSettingsOpen && 
              !settingsMenu.contains(e.target) && 
              e.target !== settingsBtn) {{
            isSettingsOpen = false;
            settingsMenu.classList.remove('visible');
          }}

          if (isDownloadsOpen && 
              !downloadsMenu.contains(e.target) && 
              e.target !== downloadBtn) {{
            isDownloadsOpen = false;
            downloadsMenu.classList.remove('visible');
          }}
        }});

        // Mouse interaction handlers
        videoWrapper.addEventListener('mousemove', showControlsTemporarily);
        videoWrapper.addEventListener('mouseleave', () => {{
          if (!isDragging && !videoPlayer.paused && !isSettingsOpen && !isDownloadsOpen) {{
            customControls.classList.remove('active');
          }}
        }});

        videoPlayer.addEventListener('pause', () => {{
          customControls.classList.add('active');
          playPauseBtn.innerHTML = '<i class="material-icons">play_arrow</i>';
          isPlaying = false;
        }});

        videoPlayer.addEventListener('contextmenu', (e) => {{
          e.preventDefault();
          return false;
        }});

        // Video loading event handlers
        videoPlayer.addEventListener('canplay', () => {{
          showUnifiedNotification("", {{ hideSpinner: true, showToast: false }});

          if (isPlaying) {{
            videoPlayer.play().catch(err => console.error("Error playing video:", err));
            playPauseBtn.innerHTML = '<i class="material-icons">pause</i>';
          }}
        }});

        videoPlayer.addEventListener('waiting', () => {{
          showUnifiedNotification("Loading video...", {{ 
            showSpinner: true, 
            showToast: false 
          }});
        }});

        videoPlayer.addEventListener('playing', () => {{
          showUnifiedNotification("", {{ hideSpinner: true, showToast: false }});
          playPauseBtn.innerHTML = '<i class="material-icons">pause</i>';
          isPlaying = true;
        }});

        // Download button event listeners
        downloadClipBtn.addEventListener('click', downloadCurrentClip);
        downloadPlaylistBtn.addEventListener('click', downloadAllClips);
        playlistSettingsExpander.addEventListener('click', togglePlaylistSettingsExpander);
        enableAllClipsBtn.addEventListener('click', enableAllClips);
        disableAllClipsBtn.addEventListener('click', disableAllClips);

        // Initialize player
        const activeVideos = getActiveVideos();
        if (activeVideos.length > 0) {{
          loadVideo(activeVideos[0]);
          // Set initial playing state
          isPlaying = true;
        }}

        updateMuteButtonText();
        updateSidebar();

        // Streamlit resize handling
        window.addEventListener('resize', function() {{
          window.setTimeout(function() {{
            window.parent.postMessage({{
              type: 'streamlit:setFrameHeight',
              height: document.body.scrollHeight
            }}, '*');
          }}, 100);
        }});

        window.parent.postMessage({{
          type: 'streamlit:setFrameHeight',
          height: document.body.scrollHeight
        }}, '*');
      </script>
    </body>
    </html>
    """

    # Render the HTML component with responsive width
    components.html(html_code, height=1500, scrolling=False)
