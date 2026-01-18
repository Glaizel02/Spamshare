import express from 'express';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const app = express();
const __dirname = path.dirname(fileURLToPath(import.meta.url));

app.use(express.json());
app.use(express.static('public'));

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.post('/start', (req, res) => {
    const { cookie, link, limit } = req.body;

    // This runs your EXACT node index.js file
    const child = spawn('node', ['index.js']);

    // This "types" the inputs into your script's readline-sync prompts
    child.stdin.write(`1\n`); // Tells it "1" cookie
    child.stdin.write(`${cookie}\n`); // Pastes the cookie
    child.stdin.write(`${link}\n`); // Pastes the link
    child.stdin.write(`${limit}\n`); // Pastes the limit
    child.stdin.end();

    child.stdout.on('data', (data) => {
        console.log(`Script Output: ${data}`);
    });

    res.json({ status: "Script triggered! check Railway logs." });
});

app.listen(process.env.PORT || 3000);
