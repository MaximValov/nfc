import streamlit as st
import json
from streamlit.components.v1 import html

st.title("📱 Mobile NFC Reader/Writer")
st.markdown("""
### **Read & Write NFC tags directly from your phone!**  
✅ **Works on Chrome for Android (Android 8+)**  
❌ **Does not work on iOS (Apple restricts Web NFC)**  
""")

# NFC Read/Write Functions (JavaScript)
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

            // Send data back to Streamlit
            window.parent.postMessage({
                type: 'NFC_READ_RESULT',
                data: records
            }, '*');
        };
    } catch (error) {
        window.parent.postMessage({
            type: 'NFC_ERROR',
            error: error.toString()
        }, '*');
    }
}

async function writeNFC(text) {
    try {
        const writer = new NDEFWriter();
        await writer.write(text);
        window.parent.postMessage({
            type: 'NFC_WRITE_SUCCESS'
        }, '*');
    } catch (error) {
        window.parent.postMessage({
            type: 'NFC_ERROR',
            error: error.toString()
        }, '*');
    }
}
</script>
"""

# Inject JavaScript into the page
html(nfc_script)

# UI for Reading NFC
st.header("🔍 Read NFC Tag")
if st.button("Read Tag"):
    read_script = """
    <script>
    readNFC();
    </script>
    """
    html(read_script)

# UI for Writing NFC
st.header("✏️ Write to NFC Tag")
text_to_write = st.text_area("Enter text to write:")
if st.button("Write Tag") and text_to_write:
    write_script = f"""
    <script>
    writeNFC(`{text_to_write}`);
    </script>
    """
    html(write_script)

# Handle NFC responses via JavaScript
response_handler = """
<script>
window.addEventListener('message', (event) => {
    if (event.data.type === 'NFC_READ_RESULT') {
        alert('Read Success! Data: ' + JSON.stringify(event.data.data));
    }
    if (event.data.type === 'NFC_WRITE_SUCCESS') {
        alert('Write Success!');
    }
    if (event.data.type === 'NFC_ERROR') {
        alert('Error: ' + event.data.error);
    }
});
</script>
"""
html(response_handler)

# Instructions
st.markdown("""
### **How to Use:**
1. Open this page in **Chrome on Android**.
2. Tap **"Read Tag"** and hold an NFC tag near your phone.
3. To write, enter text and tap **"Write Tag"**, then hold an NFC tag near your phone.

### **Requirements:**
✔ **Android 8+**  
✔ **Chrome 89+**  
✔ **NFC-enabled phone**  
✔ **NFC tags (not read-only)**  
""")