# Hotel Booking Agent

A command-line interface tool for searching and booking hotels with advanced filtering capabilities.

## Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)
- OpenAI API key

## Installation

### Option 1: Local Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/hotel-booking-cli.git
cd hotel-booking-cli
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API key:
```plaintext
OPENAI_API_KEY=your_api_key_here
```

### Option 2: Docker Installation

Build the Docker image:
```bash
docker build -t hotel-booking-cli .
```

## Usage

### Search for Hotels

Basic search command structure:
```bash
docker run -it --env-file .env -v ${PWD}/cache:/app/cache hotel-booking-cli search [CITIES] [OPTIONS]
```

Example search with all parameters:
```bash
docker run -it --env-file .env -v ${PWD}/cache:/app/cache hotel-booking-cli search "Mumbai, Delhi" \
    --checkin 2025-03-02 \
    --checkout 2025-04-05 \
    --adults 10 \
    --rooms 4 \
    --budget 5000000 \
    --preferences "pool,wifi"
```

### Parameters Explained

- `CITIES`: Comma-separated list of cities to search (e.g., "Mumbai, Delhi")
- `--checkin`: Check-in date (YYYY-MM-DD format)
- `--checkout`: Check-out date (YYYY-MM-DD format)
- `--adults`: Number of adult guests
- `--rooms`: Number of rooms required
- `--budget`: Maximum budget in local currency
- `--preferences`: Comma-separated list of amenities (e.g., "pool,wifi")

### Cache Management

The tool uses a local cache directory to store search results. Mount it using:
```bash
-v ${PWD}/cache:/app/cache
```

## Project Structure

```plaintext
hotel-booking-cli/
├── src/
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

## Dependencies

See `requirements.txt` for the complete list of dependencies.
