import 'package:flutter/material.dart';

import '../models/prediction.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';
import '../widgets/error_banner.dart';
import '../widgets/result_card.dart';

/// Main screen for ticket classification.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, this.apiService});

  final ApiService? apiService;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final ApiService _apiService;
  final TextEditingController _ticketController = TextEditingController();

  bool _isLoading = false;
  PredictionResult? _result;
  String? _errorMessage;

  static const List<String> _sampleTickets = [
    'I cannot login to my account.',
    'Payment was deducted twice.',
    'How can I change my password?',
    "My order hasn't arrived.",
    'App crashes after opening.',
  ];

  @override
  void initState() {
    super.initState();
    _apiService = widget.apiService ?? ApiService();
  }

  @override
  void dispose() {
    _ticketController.dispose();
    if (widget.apiService == null) {
      _apiService.dispose();
    }
    super.dispose();
  }

  Future<void> _classifyTicket() async {
    final ticket = _ticketController.text.trim();
    if (ticket.isEmpty) {
      setState(() {
        _errorMessage = 'Please enter a support ticket before predicting.';
        _result = null;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final result = await _apiService.classifyTicket(ticket);
      if (!mounted) return;
      setState(() {
        _result = result;
        _isLoading = false;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.message;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage =
            'Unable to reach the server. Ensure the backend is running at '
            '${AppConstants.apiBaseUrl}.';
        _isLoading = false;
      });
    }
  }

  void _useSample(String sample) {
    _ticketController.text = sample;
    setState(() {
      _errorMessage = null;
      _result = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isWide = MediaQuery.sizeOf(context).width >= 720;

    return Scaffold(
      appBar: AppBar(
        title: const Text(AppConstants.appTitle),
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 2,
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: SingleChildScrollView(
              padding: EdgeInsets.symmetric(
                horizontal: isWide ? 32 : 20,
                vertical: 24,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Classify customer support tickets instantly using AI.',
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 24),
                  TextField(
                    controller: _ticketController,
                    maxLines: 5,
                    minLines: 3,
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => _classifyTicket(),
                    decoration: InputDecoration(
                      labelText: 'Support Ticket',
                      hintText: 'Describe the customer issue...',
                      alignLabelWithHint: true,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      filled: true,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _sampleTickets.map((sample) {
                      return ActionChip(
                        label: Text(
                          sample.length > 36
                              ? '${sample.substring(0, 36)}...'
                              : sample,
                        ),
                        onPressed: _isLoading ? null : () => _useSample(sample),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    height: 48,
                    child: FilledButton.icon(
                      onPressed: _isLoading ? null : _classifyTicket,
                      icon: _isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.auto_awesome),
                      label: Text(_isLoading ? 'Classifying...' : 'Predict'),
                    ),
                  ),
                  if (_errorMessage != null) ...[
                    const SizedBox(height: 20),
                    ErrorBanner(
                      message: _errorMessage!,
                      onDismiss: () => setState(() => _errorMessage = null),
                    ),
                  ],
                  if (_result != null) ...[
                    const SizedBox(height: 24),
                    ResultCard(result: _result!),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
