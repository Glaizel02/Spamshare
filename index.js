import axios from "axios";

import fs from "fs-extra";

import chalk from "chalk";

import readline from "readline-sync";



// Random UA

const ua_list = [

"Mozilla/5.0 (Linux; Android 10; Wildfire E Lite...)",

"Mozilla/5.0 (Linux; Android 11; KINGKONG 5 Pro...)",

"Mozilla/5.0 (Linux; Android 11; G91 Pro...)"

];

const ua = ua_list[Math.floor(Math.random() * ua_list.length)];



axios.defaults.timeout = 10000;



// Banner

function banner() {

console.clear();

console.log(chalk.blue(`

██████╗ ██╗ █████╗ ██╗███████╗

██╔════╝ ██║ ██╔══██╗██║╚══███╔╝

██║ ███╗██║ ███████║██║ ███╔╝

██║ ██║██║ ██╔══██║██║ ███╔╝

╚██████╔╝███████╗██║ ██║██║███████╗

╚═════╝ ╚══════╝╚═╝ ╚═╝╚═╝╚══════╝

`));

console.log(chalk.cyan("Author : glaiz (author all)"));

console.log(chalk.cyan("Facebook: facebook.com/glaiz"));

console.log(chalk.cyan("GitHub : github.com/glaiz1"));

console.log(chalk.gray("---------------------------------------------------"));

}



async function login() {

banner();

console.log(chalk.yellow("Lagay mo rito fb cookie mo tanga (pwede multiple)"));



let num = parseInt(readline.question(chalk.green("Ilang cookies? ")));

if (isNaN(num)) return login();



let tokens = [];

let cookies_store = [];



for (let i = 0; i < num; i++) {

let cookieInput = readline.question(chalk.green(`cookie ${i+1}: `));

let cookie = {};



cookieInput.split("; ").forEach(val => {

let s = val.split("=");

if (s[0] && s[1]) cookie[s[0]] = s[1];

});



try {

const res = await axios.get("https://business.facebook.com/business_locations", {

headers: {

"user-agent": ua,

"referer": "https://www.facebook.com/",

Cookie: cookieInput

},

withCredentials: true

});



let tokenMatch = res.data.match(/(EAAG\w+)/);

if (!tokenMatch) {

console.log(chalk.red(`❌ Token extraction failed for cookie ${i+1}`));

continue;

}



let token = tokenMatch[1];

tokens.push(token);

cookies_store.push(cookie);

console.log(chalk.green(`\n✅ Token found: ${token}`));



} catch (e) {

console.log(chalk.red(`Error parsing cookie ${i+1}: ${e.message}`));

}

}



if (!tokens.length) return console.log(chalk.red("Walang valid, try again")), login();



fs.writeFileSync("tokens.json", JSON.stringify(tokens));

fs.writeFileSync("cookies.json", JSON.stringify(cookies_store));



await bot();

}



async function sharePost(token, cookie, link, n, start) {

try {

const res = await axios.post(

`https://www.facebook.com/manwelsoyasistayob`,

{},

{ headers: { "user-agent": ua, Cookie: Object.entries(cookie).map(x => x.join("=")).join("; ") } }

);



if (res.data.id) {

let diff = Math.floor((Date.now() - start) / 1000);

console.log(chalk.green(`*--> ${n}. Shared (${diff}s)`));

return true;

} else {

console.log(chalk.red(`*--> ${n} Failed: ${JSON.stringify(res.data)}`));

return false;

}

} catch (e) {

console.log(chalk.red(`*--> ${n} Error: ${e.message}`));

return false;

}

}



async function bot() {

banner();

if (!fs.existsSync("tokens.json")) return login();



const tokens = JSON.parse(fs.readFileSync("tokens.json"));

const cookies = JSON.parse(fs.readFileSync("cookies.json"));



let link = readline.question(chalk.cyan("Link ng post: "));

let limit = parseInt(readline.question(chalk.cyan("Limitasyon: ")));



console.log(chalk.yellow("Loading..."));



const start = Date.now();

const chunk = 40;

let n = 1;



while (n <= limit) {

let batch = [];

for (let i = 0; i < chunk && n <= limit; i++, n++) {

let randomIndex = Math.floor(Math.random() * tokens.length);

batch.push(sharePost(tokens[randomIndex], cookies[randomIndex], link, n, start));

}

await Promise.allSettled(batch);

if (n <= limit) {

console.log(chalk.yellow(`Cooldown 10s...`));

await new Promise(r => setTimeout(r, 10000));

}

}

console.log(chalk.green("Tapos na lahat ng share!"));

}



login();
