MONACO_EDITOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monaco Editor</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
            background-color: #000000;
        }
        #container {
            height: 100%;
            width: 100%;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js"></script>
</head>
<body>
    <div id="container"></div>
    <script>
        let editor = null;
        let initialCode = "";
        let initialLanguage = "python";

        require.config({
            paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }
        });

        require(['vs/editor/editor.main'], function() {
            monaco.editor.defineTheme('notebook-black', {
                base: 'vs-dark',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#000000',
                    'editor.lineHighlightBackground': '#111111',
                    'editorGutter.background': '#000000',
                    'editorLineNumber.foreground': '#444444',
                    'editorLineNumber.activeForeground': '#007acc'
                }
            });

            editor = monaco.editor.create(document.getElementById('container'), {
                value: initialCode,
                language: initialLanguage,
                theme: 'notebook-black',
                automaticLayout: true,
                fontSize: 14,
                fontFamily: "'Fira Code', 'Consolas', 'Courier New', monospace",
                lineNumbers: 'on',
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                renderWhitespace: 'selection',
                tabSize: 4,
                insertSpaces: true,
                smoothScrolling: true,
                cursorBlinking: 'smooth',
                cursorSmoothCaretAnimation: 'on',
                folding: true,
                bracketPairColorization: { enabled: true }
            });

            window.addEventListener('resize', function() {
                if (editor) {
                    editor.layout();
                }
            });
        });

        function monacoSetContent(content) {
            initialCode = content;
            if (editor) {
                editor.setValue(content);
            }
        }

        function monacoGetContent() {
            return editor ? editor.getValue() : initialCode;
        }

        function monacoSetLanguage(language) {
            initialLanguage = language;
            if (editor && window.monaco) {
                monaco.editor.setModelLanguage(editor.getModel(), language);
            }
        }
    </script>
</body>
</html>
"""
