# Gitlab XSS & CSP Bypass on Commit Page - ATO - POC Code

0-day as of Tuesday, May 13, 2025. Version - 17.11.2 - 90+ days since report at February 4, 2025. I guess it's a 3 month old duplicate. Severity is somewhere between 8.0 and 9.0.

## Video POC - XSS

[![PoC Video](https://img.youtube.com/vi/xEB7v0Ye7pE/maxresdefault.jpg)](https://youtu.be/xEB7v0Ye7pE)

## Video POC - ATO

[![PoC Video](https://img.youtube.com/vi/rzFndaPhj2k/maxresdefault.jpg)](https://youtu.be/rzFndaPhj2k)

## Quick Start

1. Clone the repository:

```
git clone https://github.com/justas-b1/gitlab-xss.git
cd gitlab-xss
```

2. Modify the xss.txt or ato.txt file.

3. Run - XSS
```
python poc.py --url "https://gitlab.com/group/project/-/commit/49d1bf57b239f06b87d317868anmnc3447e59581" --session "YOUR_SESSION_COOKIE_VALUE" --file xss.txt
```

4. Run - ATO
```
python poc.py --url "https://gitlab.com/group/project/-/commit/49d1bf57b239f06b87d317868anmnc3447e59581" --session "YOUR_SESSION_COOKIE_VALUE" --file ato.txt
```

### 🔍 How to Find _gitlab_session in Request Headers (Using Browser DevTools)

You can find your GitLab session cookie (_gitlab_session) by inspecting the request headers of a network request.

<details> <summary>🔽 Click To Expand</summary>

1. 🧑‍💻 Log in to GitLab in your browser.
2. 🛠️ Press F12 or Right-click → Inspect to open Developer Tools.
3. 🌐 Go to the Network tab.
4. 🔁 Refresh the page to load requests.
5. 📄 Click on any request.
6. 📥 In the Headers section, scroll down to Request Headers → look for the Cookie header.
7. 🍪 Find the cookie named _gitlab_session — that's your active session cookie.

It looks something like:

```
_gitlab_session=abcdef1234567890abcdef1234567890...
```

</details>

## Explanation - XSS

json:table allows HTML injection using "isHtmlSafe": true attribute. This combined with data-blob-diff-path leads to XSS and CSP bypass on commit page.

The data-blob-diff-path="partial_url" takes the raw HTML contents of https://gitlab.com/partial_url response and appends it on page.

## Explanation - Arbitrary POST Request - ATO

data-award-url from https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/assets/javascripts/notes/components/noteable_note.vue

Can be combined with HTML injection to send arbitrary POST requests to various critical endpoints like /-/profile/emails? (adds a secondary email to users account) and /api/v4/users? (if the victim is admin, it creates a new verified admin account, there's no 2FA or any kind of additional protection).

Victim clicks on invisible, full page overlay -> payload sends a POST request that adds secondary email (which is attacker controlled) -> attacker can then go to that secondary email, follow the confirmation link -> then use confirmed secondary email to change password and remove primary email (locking victim out of their account).

## Steps To Reproduce - XSS

1. Create a project.
2. Create a HTML file with XSS payload: <script>alert(document.domain)</script>
3. Copy the HTML files partial raw path, example: /group/project/-/raw/main/test.html and modify xss.txt payload.
4. Create any merge request and go to commit page (a page where file diffs are located).
5. Add a comment with modified xss.txt payload.
6. After some time, the auto refresh should render payload for both attacker and victim (and anyone who has the commit page opened in any of browser tabs).
7. If victim clicks on invisible, full page overlay, payload triggers.

## Steps To Reproduce - Arbitrary POST Request - ATO, New Admin Account, SSH Key

1. Post a comment with any of these payloads.
2. Admin.txt payload only works if victim has admin privileges, not likely, but potentially devastating since it automatically creates new verified admin account, which can then delete other admins.
3. ssh.txt payload adds a new ssh key to victims account.

Or run the script.

## 🛠️ GitLab Commit Note Poster (Automated Script)

This script allows you to post notes to GitLab commit pages using the GitLab web interface (not the API) by simulating browser behavior with curl. It supports:

- Session authentication via _gitlab_session cookie
- Automatic CSRF token extraction
- Periodic, repeated note posting
- Reading note content from a local text file

## ⚙️ What the Script Does

| Step                          | Description                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| 🔗 **URL Parsing**            | Takes a full GitLab commit URL and extracts domain, namespace, and commit ID.        |
| 🔐 **Authentication**         | Uses the provided `_gitlab_session` cookie to authenticate like a logged-in browser. |
| 🛡️ **CSRF Token Extraction** | Sends a GET request to the commit page and extracts the `<meta name="csrf-token">`.  |
| 📤 **Note Posting**           | Sends a `POST` request to submit a note on the commit using the token and session.   |
| ♻️ **Looping**                | Continuously re-posts the note at a user-defined interval (default 60s).             |

## 📦 Script Arguments

| Argument     | Required                   | Description                                                                  |
| ------------ | -------------------------- | ---------------------------------------------------------------------------- |
| `--url`      | ✅ Yes                      | Full GitLab commit URL (e.g. `https://gitlab.com/group/repo/-/commit/<SHA>`) |
| `--session`  | ✅ Yes                      | Value of your `_gitlab_session` cookie from browser                          |
| `--file`     | ❌ No (default: `text.txt`) | Path to a local file containing the note body (multiline supported)          |
| `--interval` | ❌ No (default: `60`)       | Interval in seconds to re-post the note repeatedly                           |

## 🧪 Example Usage

```
python gitlab_note.py \
  --url https://gitlab.com/group/project/-/commit/<SHA> \
  --session YOUR_SESSION_COOKIE_VALUE \
  --file xss.txt \
  --interval 30
```

## 💡 Company Information

GitLab is a web-based DevOps platform that provides an integrated CI/CD pipeline, enabling developers to plan, develop, test, and deploy code seamlessly. Key features include:

- Version Control (Git)
- Issue Tracking 🐛
- Code Review 🔍
- CI/CD Automation 🚀

## 🏢 Who Uses GitLab?

GitLab is trusted by companies of all sizes, from startups to enterprises, including:

| Company                                            | Industry                  | Description                                                                                                                   |
| -------------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [Goldman Sachs](https://www.goldmansachs.com/)     | Finance 💵                | A global investment bank using GitLab to modernize software pipelines and improve developer efficiency.                       |
| [Siemens](https://www.siemens.com/)                | Engineering ⚙️            | A global tech powerhouse leveraging GitLab for collaborative development in industrial automation and digital infrastructure. |
| [NVIDIA](https://www.nvidia.com/)                  | Technology 💻             | A leader in GPUs and AI computing, NVIDIA uses GitLab for scalable CI/CD and code management.                                 |
| [T-Mobile](https://www.t-mobile.com/)              | Telecommunications 📱     | Uses GitLab to manage internal tools and rapidly deliver new digital services to customers.                                   |
| [NASA](https://www.nasa.gov/)                      | Aerospace 🚀              | NASA utilizes GitLab for managing mission-critical code in scientific and engineering applications.                           |
| [Sony](https://www.sony.com/)                      | Entertainment 🎮          | Uses GitLab to support development workflows across gaming, electronics, and entertainment platforms.                         |
| [UBS](https://www.ubs.com/)                        | Banking 🏦                | A Swiss banking giant leveraging GitLab for secure, compliant DevOps in financial applications.                               |
| [Lockheed Martin](https://www.lockheedmartin.com/) | Defense & Aerospace 🛡️   | Employs GitLab for secure software development in defense systems and space technologies.                                     |
| [Shopify](https://www.shopify.com/)                | E-commerce 🛒             | Uses GitLab to scale DevOps practices and support its cloud-based e-commerce platform.                                        |
| [ING](https://www.ing.com/)                        | Financial Services 💳     | A Dutch bank adopting GitLab to improve developer collaboration and accelerate delivery.                                      |
| [CERN](https://home.cern/)                         | Scientific Research 🔬    | The European Organization for Nuclear Research uses GitLab to coordinate complex software across global teams.                |
| [Splunk](https://www.splunk.com/)                  | Data Analytics 📊         | Relies on GitLab for managing code and automating builds in its data platform ecosystem.                                      |
| [Comcast](https://corporate.comcast.com/)          | Media & Communications 📺 | Uses GitLab to streamline application delivery across their massive entertainment and broadband network.                      |
| [Deutsche Telekom](https://www.telekom.com/)       | Telecommunications 🌍     | Applies GitLab for agile development and managing cloud-native telecom infrastructure.                                        |
| [Alibaba](https://www.alibaba.com/)                | Tech & E-commerce 🧧      | One of the world’s largest tech firms, using GitLab to scale development across massive infrastructure.                       |

## 🛡️ GitLab in Defense

GitLab is favored by U.S. Department of Defense (DoD) agencies for secure, self-hosted DevSecOps environments, offering:

- On-Premise Deployment 🖥️
- Security & Compliance 🔒

Its ability to manage sensitive data and maintain operational control makes GitLab a key tool for government and defense sectors.

## Affected Websites

Shodan query: http.title:"GitLab"

Returns more than 50 thousand results.

![Shodan](images/shodan_gitlab_self_hosted.PNG)

## ⚠️ Legal Disclaimer  

This Proof-of-Concept (PoC) is provided **for educational purposes only**.  

- **Authorized Use Only**: Test only on systems you own or have explicit permission to assess.  
- **No Liability**: The author is not responsible for misuse or damages caused by this tool.  
- **Ethical Responsibility**: Do not use this tool to violate laws or exploit systems without consent.  

By using this software, you agree to these terms.
