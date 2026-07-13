import 'package:flutter_test/flutter_test.dart';
import 'package:support_ticket_classifier/models/prediction.dart';

void main() {
  group('PredictionResult', () {
    test('fromJson parses valid response', () {
      final result = PredictionResult.fromJson({
        'ticket': 'Payment deducted twice.',
        'category': 'Payment',
        'confidence': 0.95,
      });

      expect(result.ticket, 'Payment deducted twice.');
      expect(result.category, 'Payment');
      expect(result.confidence, 0.95);
      expect(result.confidencePercentage, '95.0%');
    });
  });
}
