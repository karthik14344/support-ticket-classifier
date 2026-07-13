# Support Ticket Classifier - Flutter Client

Flutter frontend for the AI-powered Support Ticket Classification System.

## Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) (3.2+)
- Running FastAPI backend (default: `http://localhost:8000`)

## Setup

```bash
cd frontend/flutter_app
flutter pub get
```

## Run

### Web (quickest for local testing)

```bash
flutter run -d chrome
```

### Windows Desktop

```bash
flutter run -d windows
```

### Android Emulator

The Android emulator cannot reach `localhost` on your host machine. Use:

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

### Custom API URL

```bash
flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
```

## Project Structure

```
lib/
├── main.dart
├── models/
│   └── prediction.dart
├── screens/
│   └── home_screen.dart
├── services/
│   └── api_service.dart
├── utils/
│   └── constants.dart
└── widgets/
    ├── error_banner.dart
    └── result_card.dart
```

## Features

- Ticket text input with sample chips
- Loading indicator during API calls
- Result card with category and confidence
- Error handling for network and API failures
- Responsive layout for mobile and desktop widths
