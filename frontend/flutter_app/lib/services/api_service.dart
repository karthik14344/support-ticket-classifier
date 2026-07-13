import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/prediction.dart';
import '../utils/constants.dart';

/// Exception thrown when API communication fails.
class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

/// HTTP client for the Support Ticket Classifier backend.
class ApiService {
  ApiService({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConstants.apiBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  Uri _uri(String path) => Uri.parse('$_baseUrl$path');

  /// Classify a support ticket via POST /classify.
  Future<PredictionResult> classifyTicket(String ticket) async {
    final response = await _client
        .post(
          _uri(AppConstants.classifyEndpoint),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'ticket': ticket}),
        )
        .timeout(AppConstants.requestTimeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return PredictionResult.fromJson(data);
    }

    String message = 'Classification failed (${response.statusCode}).';
    try {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      if (body['detail'] != null) {
        message = body['detail'].toString();
      }
    } catch (_) {
      // Keep default message if response body is not JSON.
    }

    throw ApiException(message, statusCode: response.statusCode);
  }

  /// Check backend health via GET /health.
  Future<bool> checkHealth() async {
    final response = await _client
        .get(_uri(AppConstants.healthEndpoint))
        .timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      return false;
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return data['status'] == 'healthy';
  }

  void dispose() {
    _client.close();
  }
}
