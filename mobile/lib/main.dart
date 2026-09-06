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
  String _panel = 'AZNet new tab. Phase 1 research shell — not Chromium.';
  String _airlock = 'download → scan → scrub → verify → vault';

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
        _panel = 'AZNet / Lamb Lens refused (advisory).';
      });
      _receipt('ethics_refuse');
      return;
    }
    setState(() {
      _panel = q.contains('.') && !q.contains(' ')
          ? 'Sandbox preview receipted for $q (not Chromium).'
          : 'AZNet ethical search for "$q". Cite sources. Advisory.';
    });
    _receipt(q.contains('.') ? 'navigate' : 'ethical_search');
  }

  void _home() {
    _omnibox.clear();
    setState(() => _panel = 'Home — everblooming sigil. AZNet new tab.');
    _receipt('home');
  }

  void _airlockGo() {
    setState(() {
      _airlock =
          'download · scan · scrub · verify · vault — metadata only on device.';
      _panel = 'Airlock ran. No receipt = no action.';
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
          const Text(
            'No receipt = no action.',
            style: TextStyle(color: kGold, fontStyle: FontStyle.italic, fontSize: 16),
          ),
          const SizedBox(height: 8),
          const Text(
            'On-device Phase 1 research shell. AZNet / Lamb Lens. '
            'Not Chromium. AZMail is a sibling product, not this app.',
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              IconButton(onPressed: () => _receipt('back'), icon: const Icon(Icons.arrow_back)),
              IconButton(onPressed: () => _receipt('forward'), icon: const Icon(Icons.arrow_forward)),
              IconButton(onPressed: () => _receipt('reload'), icon: const Icon(Icons.refresh)),
              IconButton(onPressed: _home, icon: const Icon(Icons.home)),
            ],
          ),
          TextField(
            controller: _omnibox,
            decoration: const InputDecoration(labelText: 'AZNet search or URL'),
            onSubmitted: (_) => _go(),
          ),
          const SizedBox(height: 12),
          FilledButton(onPressed: _go, child: const Text('Go')),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: _airlockGo, child: const Text('Airlock')),
          const SizedBox(height: 12),
          Text(_panel, style: const TextStyle(color: kGold)),
          const SizedBox(height: 8),
          Text(_airlock),
          const SizedBox(height: 16),
          const Text('Receipts', style: TextStyle(color: kGold)),
          for (final r in _receipts.take(12))
            Card(
              margin: const EdgeInsets.only(top: 8),
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: SelectableText(r, style: const TextStyle(fontFamily: 'monospace', fontSize: 12)),
              ),
            ),
        ],
      ),
    );
  }
}
