export function installNodeFileReader() {
  if (globalThis.FileReader) return;

  globalThis.FileReader = class FileReader {
    result = null;
    error = null;
    onload = null;
    onloadend = null;
    onerror = null;

    readAsArrayBuffer(blob) {
      blob
        .arrayBuffer()
        .then((result) => {
          this.result = result;
          const event = { target: this };
          this.onload?.(event);
          this.onloadend?.(event);
        })
        .catch((error) => {
          this.error = error;
          this.onerror?.(error);
          this.onloadend?.({ target: this });
        });
    }

    readAsDataURL(blob) {
      blob
        .arrayBuffer()
        .then((result) => {
          const base64 = Buffer.from(result).toString('base64');
          this.result = `data:${blob.type || 'application/octet-stream'};base64,${base64}`;
          const event = { target: this };
          this.onload?.(event);
          this.onloadend?.(event);
        })
        .catch((error) => {
          this.error = error;
          this.onerror?.(error);
          this.onloadend?.({ target: this });
        });
    }
  };
}
