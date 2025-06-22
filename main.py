import streamlit as st
from streamlit.components.v1 import html
import json

st.title("📱 Mobile NFC Reader/Writer (Improved)")

# Session state to store NFC data
if 'nfc_data' not in st.session_state:
    st.session_state.nfc_data = None
if 'nfc_error' not in st.session_state:
    st.session_state.nfc_error = None

# JavaScript NFC handler
nfc_script = """
<script>
async function readNFC() {
    try {
        const reader = new NDEFReader();
        await reader.scan();

        reader.onreading = event => {
            const decoder = new TextDecoder();
            let records = [];

            for (const record of event.message.records) {
                records.push({
                    type: record.recordType,
                    data: decoder.decode(record.data)
                });
            }

            // Send to Streamlit via URL hash
            window.location.hash = "nfc_data=" + encodeURIComponent(JSON.stringify(records));
        };
    } catch (error) {
        window.location.hash = "nfc_error=" + encodeURIComponent(error.toString());
    }
}

async function writeNFC(text) {
    try {
        const writer = new NDEFWriter();
        await writer.write(text);
        window.location.hash = "nfc_write_success=true";
    } catch (error) {
        window.location.hash = "nfc_error=" + encodeURIComponent(error.toString());
    }
}
</script>
"""
html(nfc_script)

# Check URL hash for NFC results
if st.experimental_get_query_params().get("nfc_data"):
    st.session_state.nfc_data = json.loads(st.experimental_get_query_params()["nfc_data"][0])
    st.experimental_set_query_params()  # Clear params after reading

if st.experimental_get_query_params().get("nfc_error"):
    st.session_state.nfc_error = st.experimental_get_query_params()["nfc_error"][0]
    st.experimental_set_query_params()

if st.experimental_get_query_params().get("nfc_write_success"):
    st.success("✅ NFC tag written successfully!")
    st.experimental_set_query_params()

# Display area
st.header("🔍 NFC Data")
if st.session_state.nfc_data:
    st.json(st.session_state.nfc_data)
elif st.session_state.nfc_error:
    st.error(f"Error: {st.session_state.nfc_error}")

# Read/Write buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("📖 Read NFC Tag"):
        html("<script>readNFC();</script>")

with col2:
    text_to_write = st.text_input("Text to write:")
    if st.button("✏️ Write NFC Tag") and text_to_write:
        html(f"<script>writeNFC(`{text_to_write}`);</script>")