# Receipt Parsing Web API

This project provides a web API for parsing receipt images and extracting structured data.

## Project Overview

The API is built with FastAPI and uses a pre-trained Donut model for receipt parsing. It can extract information such as merchant name, address, items, and totals from a receipt image.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/receipt-parser.git
    cd receipt-parser
    ```

2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```

## Running the API

To run the development server, use the following command:

```bash
poetry run uvicorn api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Usage

The API provides both **asynchronous** and **synchronous** receipt parsing endpoints.

### Async Flow (Default)

Submit a receipt for background processing and poll for results.

**1. Upload Receipt**

-   **Method:** `POST`
-   **URL:** `/receipts`
-   **Body:** `multipart/form-data` with:
    -   `file`: receipt image (JPEG, PNG, or TIFF)
    -   `metadata` (optional): JSON object with custom metadata

**Example:**

```bash
curl -X POST -F "file=@receipt.jpg" \
  -F 'metadata={"source":"mobile"}' \
  http://127.0.0.1:8000/receipts
```

**Response (202 Accepted):**

```json
{
  "job_id": "a1b2c3...",
  "status_url": "http://127.0.0.1:8000/receipts/a1b2c3.../status",
  "estimated_seconds": 5
}
```

**2. Check Status**

-   **Method:** `GET`
-   **URL:** `/receipts/{job_id}/status`

```bash
curl http://127.0.0.1:8000/receipts/a1b2c3.../status
```

**3. Retrieve Result**

-   **Method:** `GET`
-   **URL:** `/receipts/{job_id}`

```bash
curl http://127.0.0.1:8000/receipts/a1b2c3...
```

**Response (200 OK when completed):**

```json
{
  "job_id": "a1b2c3...",
  "status": "completed",
  "parsed": {
    "invoice_id": "...",
    "merchant": {
      "name": "...",
      "address": "..."
    },
    "timestamp": "...",
    "currency": "EUR",
    "items": [
      {
        "description": "...",
        "qty": 1.0,
        "unit_price": 10.0,
        "total_price": 10.0,
        "vat_rate": 19
      }
    ],
    "totals": {
      "gross": 10.0,
      "payment_method": "unknown"
    },
    "meta": {}
  },
  "meta": {
    "processing_time_seconds": 2.145,
    "model_version": "donut-base-finetuned-cord-v2"
  }
}
```

### Sync Flow

For immediate results, add `?sync=true` to the upload endpoint:

```bash
curl -X POST -F "file=@receipt.jpg" \
  "http://127.0.0.1:8000/receipts?sync=true"
```

**Response (200 OK):** Returns the same completed job payload shown above
```

## Configuration

There are no specific configuration options for this API at the moment.

## Troubleshooting

-   **Model download issues:** The first time you run the application, it will download the pre-trained Donut model. If you experience issues, make sure you have a stable internet connection.
-   **Incorrect parsing:** The accuracy of the parsing depends on the quality of the receipt image. Ensure the image is clear and well-lit for best results.
