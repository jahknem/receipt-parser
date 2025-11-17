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

The primary endpoint for parsing receipts is `/parse-receipt/`.

### Request

-   **Method:** `POST`
-   **URL:** `/parse-receipt/`
-   **Body:** `multipart/form-data` with a single field named `file` containing the receipt image.

**Example using `curl`:**

```bash
curl -X POST -F "file=@/path/to/your/receipt.jpg" http://127.0.0.1:8000/parse-receipt/
```

### Response

The API returns a JSON object representing the parsed invoice.

**Example Response:**

```json
{
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
}
```

## Configuration

There are no specific configuration options for this API at the moment.

## Troubleshooting

-   **Model download issues:** The first time you run the application, it will download the pre-trained Donut model. If you experience issues, make sure you have a stable internet connection.
-   **Incorrect parsing:** The accuracy of the parsing depends on the quality of the receipt image. Ensure the image is clear and well-lit for best results.
