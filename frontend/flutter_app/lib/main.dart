import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'utils/constants.dart';

void main() {
  runApp(const SupportTicketClassifierApp());
}

/// Root application widget.
class SupportTicketClassifierApp extends StatelessWidget {
  const SupportTicketClassifierApp({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF1565C0),
      brightness: Brightness.light,
    );

    return MaterialApp(
      title: AppConstants.appTitle,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: colorScheme,
        useMaterial3: true,
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: colorScheme.surfaceContainerHighest.withValues(alpha: 0.4),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
