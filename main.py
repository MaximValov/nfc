import streamlit as st
import ndef
import nfc
import time
from threading import Thread

# App title and description
st.title("📱 NFC Tag Reader/Writer")
st.write("This app allows you to read from and write text to NFC tags using your computer's NFC reader.")

# Initialize session state variables
if 'nfc_operation' not in st.session_state:
    st.session_state.nfc_operation = None
if 'nfc_message' not in st.session_state:
    st.session_state.nfc_message = ""
if 'last_read' not in st.session_state:
    st.session_state.last_read = ""
if 'write_success' not in st.session_state:
    st.session_state.write_success = False


# Function to read NFC tag
def read_nfc_tag():
    st.session_state.nfc_operation = "read"
    st.session_state.nfc_message = "Hold an NFC tag near the reader..."
    st.session_state.last_read = ""

    def on_connect(tag):
        if tag.ndef:
            try:
                records = tag.ndef.records
                text_records = [str(record.text) for record in records if isinstance(record, ndef.TextRecord)]
                st.session_state.last_read = "\n".join(text_records)
                st.session_state.nfc_message = "Tag read successfully!"
            except Exception as e:
                st.session_state.nfc_message = f"Error reading tag: {str(e)}"
        else:
            st.session_state.nfc_message = "Tag doesn't contain NDEF data"
        return True  # Return True to keep the connection alive

    try:
        with nfc.ContactlessFrontend('usb') as clf:
            if clf.connect(rdwr={'on-connect': on_connect}):
                st.rerun()
    except Exception as e:
        st.session_state.nfc_message = f"Error: {str(e)}"
        st.rerun()


# Function to write to NFC tag
def write_nfc_tag(text_to_write):
    st.session_state.nfc_operation = "write"
    st.session_state.nfc_message = "Hold an NFC tag near the writer..."
    st.session_state.write_success = False

    def on_connect(tag):
        if tag.ndef:
            try:
                # Prepare the NDEF message
                record = ndef.TextRecord(text_to_write)
                tag.ndef.records = [record]
                st.session_state.nfc_message = "Tag written successfully!"
                st.session_state.write_success = True
            except Exception as e:
                st.session_state.nfc_message = f"Error writing to tag: {str(e)}"
        else:
            st.session_state.nfc_message = "Tag is not NDEF-formatted or is read-only"
        return True  # Return True to keep the connection alive

    try:
        with nfc.ContactlessFrontend('usb') as clf:
            if clf.connect(rdwr={'on-connect': on_connect}):
                st.rerun()
    except Exception as e:
        st.session_state.nfc_message = f"Error: {str(e)}"
        st.rerun()


# Main app layout
tab1, tab2 = st.tabs(["Read NFC Tag", "Write to NFC Tag"])

with tab1:
    st.header("Read from NFC Tag")
    if st.button("Read Tag"):
        # Start reading in a separate thread to avoid blocking
        thread = Thread(target=read_nfc_tag)
        thread.start()

    if st.session_state.nfc_operation == "read":
        st.info(st.session_state.nfc_message)
        if st.session_state.last_read:
            st.text_area("Content from NFC Tag", st.session_state.last_read, height=150)

with tab2:
    st.header("Write to NFC Tag")
    text_to_write = st.text_area("Enter text to write to NFC tag", height=150)

    if st.button("Write to Tag") and text_to_write:
        # Start writing in a separate thread to avoid blocking
        thread = Thread(target=write_nfc_tag, args=(text_to_write,))
        thread.start()

    if st.session_state.nfc_operation == "write":
        if st.session_state.write_success:
            st.success(st.session_state.nfc_message)
        else:
            st.warning(st.session_state.nfc_message)

# Instructions section
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. **For Reading**:
   - Click "Read Tag"
   - Hold an NFC tag near your reader
   - Wait for the content to appear

2. **For Writing**:
   - Enter text in the text area
   - Click "Write to Tag"
   - Hold an NFC tag near your writer
   - Wait for confirmation

**Requirements**:
- NFC reader/writer connected via USB
- Python `nfcpy` and `ndeflib` libraries installed
- Compatible NFC tags (NDEF formatted)
""")

# # Installation instructions
# st.sidebar.header("Installation Help")
# st.sidebar.markdown("""
# If you don't have the required libraries:
# ```bash
# pip install nfcpy ndeflib)