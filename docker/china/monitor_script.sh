#!/bin/bash

INPUT_DIR="/input"
OUTPUT_DIR="/output"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to process PDF files
process_pdfs() {
    for pdf_file in "$INPUT_DIR"/*.pdf; do
        if [ -f "$pdf_file" ]; then
            # Generate output filename based on input filename
            output_file="$OUTPUT_DIR/$(basename "${pdf_file%.pdf}.md")"
            echo "Processing $pdf_file..."
            magic-pdf -p "$pdf_file" -o "$OUTPUT_DIR" --method auto
            echo "Generated $output_file"
        fi
    done
}

# Monitor the input directory for new PDF files
inotifywait -m -e create --format '%w%f' "$INPUT_DIR" | while read NEWFILE; do
    if [[ "$NEWFILE" == *.pdf ]]; then
        echo "New PDF file detected: $NEWFILE. Waiting 1 minute before processing."
        sleep 60
        process_pdfs
    fi
done