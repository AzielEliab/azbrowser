import 'package:flutter/material.dart';

import 'theme.dart';

void main() {
  runApp(const AzBrowserApp());
}

class AzBrowserApp extends StatelessWidget {
  const AzBrowserApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AZBrowser',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const ResearchShellPage(),
    );
  }
}

class ResearchShellPage extends StatefulWidget {
  const ResearchShellPage({super.key});

  @override
  State<ResearchShellPage> createState() => _ResearchShellPageState();
}

class _ResearchShellPageState extends State<ResearchShellPage> {
  final _omnibox = TextEditingController();
  final _receipts = <String>[];
  String _panel = 'Search or enter a .aziel name or web address.';
  String _airlock = 'No check yet.';

  @override
  void dispose() {
    _omnibox.dispose();
    super.dispose();
  }

  void _receipt(String action) {
    final hash = action.hashCode.toRadixString(16);
    setState(() {
      _receipts.insert(0, '$action · $hash');
    });
  }

  void _go() {
    final q = _omnibox.text.trim();
    if (q.isEmpty) {
      _home();
      return;
    }
    final low = q.toLowerCase();
    if (low.contains('doxx') ||
        low.contains('home address') ||
        low.contains('ssn') ||
        low.contains('steal password') ||
        low.contains('how to hack')) {
      setState(() {
        _panel = 'Lamb Lens refused this search. It is advisory.';
      });
      _receipt('ethics_refuse');
      return;
    }
    setState(() {
      _panel = q.contains('.') && !q.contains(' ')
          ? 'Preview noted for $q. Scripts do not run on this device.'
          : 'Lamb Lens search for "$q". Cite sources. Advisory.';
    });
    _receipt(q.contains('.') ? 'navigate' : 'ethical_search');
  }

  void _home() {
    _omnibox.clear();
    setState(() => _panel = 'Search or enter a .aziel name or web address.');
    _receipt('home');
  }

  void _airlockGo() {
    setState(() {
      _airlock =
          'Downloaded, scanned, cleaned, checked, and stored. Metadata only on this device.';
      _panel = 'Check finished.';
    });
    _receipt('airlock');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AZBrowser')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('AZBrowser'),
          const SizedBox(height: 8),
          const Text(
            'On-device research shell. Search, then open. Lamb Lens is advisory.',
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              IconButton(onPressed: () => _receipt('back'), icon: const Icon(Icons.arrow_back), tooltip: 'Back'),
              IconButton(onPressed: () => _receipt('forward'), icon: const Icon(Icons.arrow_forward), tooltip: 'Forward'),
              IconButton(onPressed: () => _receipt('reload'), icon: const Icon(Icons.refresh), tooltip: 'Reload'),
              IconButton(onPressed: _home, icon: const Icon(Icons.home), tooltip: 'Home'),
            ],
          ),
          TextField(
            controller: _omnibox,
            decoration: const InputDecoration(
              labelText: 'Search or enter a .aziel name or web address',
            ),
            onSubmitted: (_) => _go(),
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: _go,
            style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
            child: const Text('Go'),
          ),
          const SizedBox(height: 12),
          Text(_panel),
          const SizedBox(height: 8),
          ExpansionTile(
            title: const Text('Tools'),
            children: [
              Align(
                alignment: Alignment.centerLeft,
                child: OutlinedButton(
                  onPressed: _airlockGo,
                  style: OutlinedButton.styleFrom(minimumSize: const Size(64, 48)),
                  child: const Text('Check this address'),
                ),
              ),
              const SizedBox(height: 8),
              Align(alignment: Alignment.centerLeft, child: Text(_airlock)),
              const SizedBox(height: 8),
            ],
          ),
          ExpansionTile(
            title: const Text('Receipts'),
            children: [
              for (final r in _receipts.take(12))
                Card(
                  margin: const EdgeInsets.only(top: 8),
                  child: Padding(
                    padding: const EdgeInsets.all(10),
                    child: SelectableText(r),
                  ),
                ),
              if (_receipts.isEmpty)
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Padding(
                    padding: EdgeInsets.only(bottom: 12),
                    child: Text('No actions yet.'),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
