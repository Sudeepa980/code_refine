require('dotenv').config();

const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

app.post('/api/analyze', async (req, res) => {

    const { code, lang, action, targetLang } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ error: "API key missing" });
    }

    let actionSpecifics = `Perform: "${action}".`;

    if (action === "convert" && targetLang) {
        actionSpecifics = `CONVERT the code from ${lang} to ${targetLang}.`;
    }

    const promptText = `
Act as CodeRefine AI.
Input Language: ${lang}
Action: ${actionSpecifics}

FORMATTING RULES:
1. Return ONLY HTML.
2. If you provide a code block, use:
<pre><code class="hljs language-${targetLang || lang}">CODE_HERE</code></pre>

CODE TO PROCESS:
${code}
`;

    try {

        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    contents: [
                        {
                            parts: [{ text: promptText }]
                        }
                    ]
                })
            }
        );

        const result = await response.json();

        if (result.error) {
            return res.status(500).json({ error: result.error.message });
        }
        
        const text = result.candidates?.[0]?.content?.parts?.[0]?.text;

if (!text) {
    return res.status(500).json({ error: "No response from Gemini" });
}

res.json({ output: text });
        

    } catch (error) {
        console.error("SERVER ERROR:", error);
        res.status(500).json({ error: error.message });
    }

});

app.listen(3000, () => {
    console.log("Server running on http://localhost:3000");
});