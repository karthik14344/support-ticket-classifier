import 'package:flutter/material.dart';

import '../models/prediction.dart';

/// Card widget displaying classification results.
class ResultCard extends StatelessWidget {
  const ResultCard({
    super.key,
    required this.result,
  });

  final PredictionResult result;

  Color _categoryColor(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    switch (result.category) {
      case 'Login Issue':
        return scheme.primary;
      case 'Payment':
        return Colors.green.shade700;
      case 'Account':
        return Colors.blue.shade700;
      case 'Delivery':
        return Colors.orange.shade800;
      case 'Technical Issue':
        return Colors.red.shade700;
      default:
        return scheme.secondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final categoryColor = _categoryColor(context);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.check_circle_outline, color: categoryColor),
                const SizedBox(width: 8),
                Text(
                  'Classification Result',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            _ResultRow(
              label: 'Predicted Category',
              value: result.category,
              valueColor: categoryColor,
            ),
            const SizedBox(height: 12),
            _ResultRow(
              label: 'Confidence Score',
              value: result.confidencePercentage,
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: result.confidence,
                minHeight: 8,
                backgroundColor: theme.colorScheme.surfaceContainerHighest,
                color: categoryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResultRow extends StatelessWidget {
  const _ResultRow({
    required this.label,
    required this.value,
    this.valueColor,
  });

  final String label;
  final String value;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 2,
          child: Text(
            label,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        Expanded(
          flex: 3,
          child: Text(
            value,
            style: theme.textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.w600,
              color: valueColor,
            ),
          ),
        ),
      ],
    );
  }
}
