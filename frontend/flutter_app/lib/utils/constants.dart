/// Application constants and configuration.
class AppConstants {
  AppConstants._();

  /// Backend API base URL.
  ///
  /// - Android emulator: use `http://10.0.2.2:8000`
  /// - iOS simulator: use `http://localhost:8000`
  /// - Physical device: use your machine's LAN IP, e.g. `http://192.168.1.10:8000`
  /// - Web/Desktop: use `http://localhost:8000`
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static const String classifyEndpoint = '/classify';
  static const String healthEndpoint = '/health';

  static const String appTitle = 'Support Ticket Classifier';
  static const Duration requestTimeout = Duration(seconds: 60);
}
