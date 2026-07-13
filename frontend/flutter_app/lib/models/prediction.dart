/// Data model for classification prediction results.
class PredictionResult {
  const PredictionResult({
    required this.ticket,
    required this.category,
    required this.confidence,
  });

  final String ticket;
  final String category;
  final double confidence;

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      ticket: json['ticket'] as String,
      category: json['category'] as String,
      confidence: (json['confidence'] as num).toDouble(),
    );
  }

  String get confidencePercentage =>
      '${(confidence * 100).toStringAsFixed(1)}%';
}
