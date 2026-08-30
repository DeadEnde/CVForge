"""CVForge — parse a CV (text / Markdown / PDF / DOCX) into structured data."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Domain detection keyword maps
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "developer": ["developer",
                 "software",
                 "engineer",
                 "programmer",
                 "fullstack",
                 "full stack",
                 "backend",
                 "frontend",
                 "front-end",
                 "react",
                 "vue",
                 "angular",
                 "python",
                 "javascript",
                 "typescript",
                 "node",
                 "java",
                 "php",
                 "laravel",
                 "web developer",
                 "api",
                 "sql",
                 "android",
                 "ios"],
    "designer": ["designer",
                 "design",
                 "ui",
                 "ux",
                 "ui/ux",
                 "figma",
                 "photoshop",
                 "illustrator",
                 "branding",
                 "brand identity",
                 "logo",
                 "graphic",
                 "visual",
                 "creative",
                 "art director",
                 "typography",
                 "prototype",
                 "wireframe",
                 "interaction design"],
    "photographer": ["photograph",
                 "photographer",
                 "photo",
                 "camera",
                 "lighting",
                 "editing",
                 "lightroom",
                 "retouch",
                 "studio",
                 "wedding"],
    "marketer": ["marketing",
                 "seo",
                 "sem",
                 "social media",
                 "growth",
                 "ads",
                 "campaign",
                 "brand manager",
                 "email marketing",
                 "crm",
                 "content"],
    "data": ["data analyst",
                 "bi ",
                 "analytics",
                 "power bi",
                 "tableau",
                 "statistic",
                 "pandas",
                 "dashboard",
                 "etl",
                 "sql"],
    "manager": ["manager",
                 "director",
                 "project manager",
                 "product manager",
                 "product owner",
                 "chef de projet",
                 "scrum",
                 "agile",
                 "leadership",
                 "team lead"],
    "teacher": ["teacher",
                 "professor",
                 "professeur",
                 "trainer",
                 "formation",
                 "education",
                 "tutor",
                 "lecturer",
                 "pedagog"],
    "finance": ["finance",
                 "financial",
                 "banking",
                 "banque",
                 "fiscal",
                 "comptabilité",
                 "investor",
                 "comptable"],
    "health": ["doctor",
                 "nurse",
                 "infirmier",
                 "medecin",
                 "médecin",
                 "pharmac",
                 "dentist",
                 "physiotherap",
                 "therapist",
                 "clinician",
                 "caregiver"],
    "engineer": ["civil engineer",
                 "mechanical engineer",
                 "electrical engineer",
                 "ingénieur",
                 "ingenieur",
                 "construction",
                 "structural",
                 "mep",
                 "site engineer",
                 "project engineer"],
    "generic": [],
    "ai": ["artificial intelligence",
                 "ai engineer",
                 "machine learning",
                 "deep learning",
                 "nlp",
                 "computer vision",
                 "llm",
                 "ml engineer",
                 "data scientist",
                 "chatbot",
                 "neural",
                 "generative ai",
                 "prompt engineer",
                 "ai model"],
    "cybersecurity": ["cybersecurity",
                 "cyber security",
                 "security analyst",
                 "penetration",
                 "pen-test",
                 "ethical hacker",
                 "infosec",
                 "it security",
                 "network security",
                 "soc analyst",
                 "cissp",
                 "vulnerability"],
    "cloud": ["cloud",
                 "aws",
                 "azure",
                 "gcp",
                 "cloud engineer",
                 "cloud architect",
                 "serverless"],
    "game": ["game developer",
                 "gamedev",
                 "unity",
                 "unreal",
                 "game design",
                 "game engine",
                 "esports",
                 "gaming",
                 "level design"],
    "blockchain": ["blockchain",
                 "web3",
                 "solidity",
                 "smart contract",
                 "crypto",
                 "bitcoin",
                 "ethereum",
                 "defi",
                 "nft",
                 "token"],
    "mobile": ["mobile developer",
                 "ios developer",
                 "android developer",
                 "react native",
                 "flutter developer",
                 "swift",
                 "kotlin",
                 "mobile app",
                 "app developer"],
    "devops": ["devops",
                 "site reliability",
                 "sre",
                 "ci/cd",
                 "ci cd",
                 "docker",
                 "kubernetes",
                 "terraform",
                 "ansible",
                 "jenkins",
                 "infrastructure",
                 "platform engineer",
                 "cloudops"],
    "robotics": ["robotics",
                 "robot",
                 "automation engineer",
                 "embedded",
                 "iot",
                 "arduino",
                 "raspberry",
                 "mechatronics",
                 "automation"],
    "support": ["customer support",
                 "support specialist",
                 "helpdesk",
                 "service desk",
                 "customer service",
                 "call center",
                 "technical support",
                 "customer care",
                 "ticket"],
    "economist": ["economist",
                 "economics",
                 "econometrics",
                 "macroeconomic",
                 "microeconomic",
                 "economic analyst",
                 "policy analyst",
                 "development economics"],
    "accounting": ["accountant",
                 "accounting",
                 "audit",
                 "auditor",
                 "tax advisor",
                 "bookkeeper",
                 "cpa",
                 "controller",
                 "payroll",
                 "comptable",
                 "fiscaliste",
                 "comptabilité"],
    "ecommerce": ["ecommerce",
                 "e-commerce",
                 "shopify",
                 "dropshipping",
                 "dropship",
                 "amazon seller",
                 "marketplace",
                 "online store",
                 "store manager",
                 "retail",
                 "merchandising",
                 "woocommerce"],
    "business": ["business",
                 "operations",
                 "operations manager",
                 "corporate",
                 "strategy",
                 "b2b",
                 "b2c"],
    "founder": ["founder",
                 "co-founder",
                 "cofounder",
                 "entrepreneur",
                 "startup",
                 "ceo",
                 "owner",
                 "self-employed",
                 "solo founder"],
    "sales": ["sales",
                 "account executive",
                 "business development",
                 "sdr",
                 "bdr",
                 "sales manager",
                 "sales representative",
                 "commercial",
                 "salesforce",
                 "closer"],
    "consulting": ["consultant",
                 "consulting",
                 "management consulting",
                 "strategy consultant",
                 "advisory"],
    "logistics": ["logistics",
                 "supply chain",
                 "warehouse",
                 "procurement",
                 "freight",
                 "transportation",
                 "customs",
                 "inventory",
                 "distribution"],
    "realestate": ["real estate",
                 "realtor",
                 "property agent",
                 "real estate agent",
                 "leasing",
                 "landlord",
                 "property management"],
    "hr": ["human resources",
                 "hr manager",
                 "recruiter",
                 "recruitment",
                 "talent acquisition",
                 "people operations",
                 "headhunter",
                 "hrbp",
                 "staffing"],
    "doctor": ["doctor",
                 "physician",
                 "medical doctor",
                 "surgeon",
                 "general practitioner",
                 "dentist",
                 "pharmacist",
                 "nurse",
                 "clinician",
                 "pediatric",
                 "gynecolog",
                 "cardiolog",
                 "radiolog",
                 "anesthesi",
                 "medecin",
                 "médecin",
                 "paramedic",
                 "physiotherap",
                 "infirmier"],
    "psychology": ["psychologist",
                 "psychology",
                 "psychiatry",
                 "psychiatrist",
                 "counselor",
                 "counsellor",
                 "mental health",
                 "psychotherapy",
                 "psychologue"],
    "nutrition": ["nutritionist",
                 "nutrition",
                 "dietitian",
                 "dietetics",
                 "diet coach",
                 "nutritionniste"],
    "fitness": ["personal trainer",
                 "fitness",
                 "gym",
                 "crossfit",
                 "athlete",
                 "sports coach",
                 "strength coach",
                 "yoga instructor",
                 "pilates"],
    "veterinary": ["veterinarian",
                 "veterinary",
                 "animal hospital",
                 "vet clinic",
                 "vétérinaire"],
    "uiux": ["ui/ux",
                 "ux designer",
                 "ui designer",
                 "product designer",
                 "interaction designer",
                 "usability",
                 "user research",
                 "ux research",
                 "ux engineer"],
    "interior": ["interior designer",
                 "interior design",
                 "space planning",
                 "interior architecture",
                 "decorator",
                 "décorateur"],
    "fashion": ["fashion",
                 "stylist",
                 "fashion designer",
                 "apparel",
                 "clothing",
                 "couture",
                 "modest fashion"],
    "videographer": ["videographer",
                 "video editor",
                 "filmmaker",
                 "cinematographer",
                 "video production",
                 "video creator"],
    "musician": ["musician",
                 "music producer",
                 "singer",
                 "songwriter",
                 "composer",
                 "dj",
                 "sound engineer",
                 "guitarist",
                 "pianist",
                 "band"],
    "artist": ["artist",
                 "fine art",
                 "fine artist",
                 "sculptor",
                 "tattoo artist",
                 "ceramics",
                 "illustration art"],
    "writer": ["writer",
                 "copywriter",
                 "author",
                 "novelist",
                 "content writer",
                 "technical writer",
                 "scriptwriter",
                 "essayist",
                 "poet",
                 "rédacteur"],
    "journalist": ["journalist",
                 "journalism",
                 "reporter",
                 "news editor",
                 "press",
                 "editor in chief",
                 "correspondent",
                 "media"],
    "translator": ["translator",
                 "translation",
                 "interpreter",
                 "localization",
                 "linguist",
                 "traducteur",
                 "linguistics"],
    "contentcreator": ["content creator",
                 "influencer",
                 "youtuber",
                 "streamer",
                 "blogger",
                 "podcast host",
                 "instagram",
                 "tiktok",
                 "creator economy",
                 "community manager"],
    "architecture": ["architect",
                 "architecture",
                 "architectural",
                 "urban planning",
                 "urban planner",
                 "landscape architect"],
    "researcher": ["researcher",
                 "research scientist",
                 "postdoc",
                 "phd candidate",
                 "phd student",
                 "academic researcher",
                 "laboratory research"],
    "scientist": ["scientist",
                 "physics",
                 "chemistry",
                 "biology",
                 "biotech",
                 "biotechnology",
                 "geology",
                 "astronomy",
                 "genetics",
                 "laboratory",
                 "microbiology",
                 "neuroscience"],
    "historian": ["historian",
                 "history",
                 "archivist",
                 "museum",
                 "heritage",
                 "archaeolog"],
    "chef": ["chef",
                 "cook",
                 "culinary",
                 "pastry chef",
                 "sous chef",
                 "head chef",
                 "kitchen",
                 "gastronomy",
                 "baker",
                 "cuisinier"],
    "hospitality": ["hospitality",
                 "hotel",
                 "waiter",
                 "waitress",
                 "bartender",
                 "barista",
                 "hostess",
                 "concierge",
                 "restaurant manager",
                 "front office",
                 "hôtellerie"],
    "tourism": ["tourism",
                 "tour guide",
                 "travel consultant",
                 "travel agency",
                 "destination",
                 "travel advisor"],
    "trades": ["electrician",
                 "plumber",
                 "carpenter",
                 "mechanic",
                 "welder",
                 "hvac",
                 "technician",
                 "handyman",
                 "mason",
                 "locksmith",
                 "glazier",
                 "tiler",
                 "auto mechanic",
                 "technicien"],
    "beauty": ["hairdresser",
                 "hair stylist",
                 "barber",
                 "beautician",
                 "esthetician",
                 "makeup artist",
                 "nail technician",
                 "salon",
                 "spa",
                 "cosmetology",
                 "coiffeur",
                 "manicure"],
    "aviation": ["pilot",
                 "aviation",
                 "flight attendant",
                 "aircraft",
                 "air traffic",
                 "captain",
                 "stewardess",
                 "airline",
                 "drone pilot"],
    "agriculture": ["farmer",
                 "agriculture",
                 "agronomy",
                 "agronomist",
                 "vineyard",
                 "harvest",
                 "livestock",
                 "greenhouse",
                 "horticultur",
                 "farming"],
    "social": ["social worker",
                 "nonprofit",
                 "non-profit",
                 "ngo",
                 "charity",
                 "humanitarian",
                 "community outreach",
                 "case manager",
                 "community development",
                 "volunteer"],
    "government": ["government",
                 "public administration",
                 "civil servant",
                 "politician",
                 "diplomacy",
                 "public policy",
                 "ministry",
                 "municipal",
                 "diplomat"],
    "legal": ["lawyer",
                 "attorney",
                 "legal",
                 "counsel",
                 "judge",
                 "notary",
                 "paralegal",
                 "barrister",
                 "solicitor",
                 "jurist",
                 "compliance",
                 "magistrat",
                 "avocat",
                 "droit"],
}

DOMAIN_LABELS = {
    "developer": "Software Developer",
    "designer": "Creative Designer",
    "photographer": "Photographer",
    "marketer": "Marketing & Growth",
    "data": "Data Professional",
    "manager": "Product / Project Manager",
    "teacher": "Educator",
    "finance": "Finance Professional",
    "health": "Healthcare Professional",
    "engineer": "Engineer",
    "generic": "Professional",
    "ai": "AI / Machine Learning Engineer",
    "cybersecurity": "Cybersecurity Professional",
    "cloud": "Cloud Engineer",
    "game": "Game Developer",
    "blockchain": "Blockchain Developer",
    "mobile": "Mobile Developer",
    "devops": "DevOps / SRE Engineer",
    "robotics": "Robotics & Automation Engineer",
    "support": "Customer Support Specialist",
    "economist": "Economist",
    "accounting": "Accountant / Auditor",
    "ecommerce": "E-commerce Specialist",
    "business": "Business & Operations",
    "founder": "Founder / Entrepreneur",
    "sales": "Sales Professional",
    "consulting": "Business Consultant",
    "logistics": "Logistics & Supply Chain",
    "realestate": "Real Estate Professional",
    "hr": "HR / Talent Acquisition",
    "doctor": "Medical Professional",
    "psychology": "Psychologist / Therapist",
    "nutrition": "Nutritionist",
    "fitness": "Fitness & Sports Coach",
    "veterinary": "Veterinarian",
    "uiux": "Product / UX Designer",
    "interior": "Interior Designer",
    "fashion": "Fashion & Styling",
    "videographer": "Video & Film Maker",
    "musician": "Musician / Producer",
    "artist": "Visual Artist",
    "writer": "Writer / Copywriter",
    "journalist": "Journalist",
    "translator": "Translator / Interpreter",
    "contentcreator": "Content Creator",
    "architecture": "Architect",
    "researcher": "Researcher",
    "scientist": "Scientist",
    "historian": "Historian",
    "chef": "Chef / Culinary Artist",
    "hospitality": "Hospitality Professional",
    "tourism": "Tourism & Travel",
    "trades": "Skilled Trades Professional",
    "beauty": "Beauty & Wellness",
    "aviation": "Aviation Professional",
    "agriculture": "Agriculture Professional",
    "social": "Social Impact Professional",
    "government": "Public Sector Professional",
    "legal": "Legal Professional",
}


@dataclass
class CVData:
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    summary: str = ""
    skills: list[str] = field(default_factory=list)
    experience: list[dict] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    domain: str = "generic"
    domain_label: str = "Professional"
    raw_sections: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s.\-()]{7,})")
URL_RE = re.compile(r"(?:https?://|www\.)[^\s\"'<>]+|github\.com/[\w-]+|linkedin\.com/in/[\w-]+")


def detect_domain(text: str) -> tuple[str, str]:
    t = text.lower()
    best, best_score = "generic", 0
    for domain, kws in DOMAIN_KEYWORDS.items():
        score = sum(t.count(kw) for kw in kws)
        # Boost: if matches appear early (summary/title), weight higher
        if score > best_score:
            best, best_score = domain, score
    return best, DOMAIN_LABELS.get(best, "Professional")


def _split_sections(text: str) -> dict[str, str]:
    """Split a raw CV text into named sections."""
    section_headers = {
        "experience": r"(experience|expérience|work history|parcours professionnel|employment)",
        "education": r"(education|formation|études|academic|diploma|degree)",
        "skills": r"(skills|compétences|technical skills|technologies|expertise)",
        "projects": r"(projects|projets|portfolio|réalisations|selected works)",
        "summary": r"(summary|profile|about|à propos|profil|objective|objectif)",
        "languages": r"(languages|langues)",
    }
    lines = text.splitlines()
    sections: dict[str, str] = {}
    current = None
    for line in lines:
        s = re.sub(r"^#{1,6}\s*", "", line.strip()).strip()  # strip md heading markers
        if not s:
            continue
        matched = None
        for key, pattern in section_headers.items():
            if re.match(rf"^{pattern}\s*:?\s*$", s, re.IGNORECASE):
                matched = key
                break
        if matched:
            current = matched
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(s)
    for k in sections:
        sections[k] = "\n".join(sections[k])
    return sections


def _simple_parse(text: str) -> dict:
    """Heuristic parser: name/title from first lines, contacts, bullets."""
    lines = [re.sub(r"^#{1,6}\s*", "", l.strip()).strip() for l in text.splitlines() if l.strip()]
    name, title = "", ""
    # Name: first plausible line that looks like a person name (2-4 words, no digits)
    for line in lines[:6]:
        if (re.fullmatch(r"[A-ZÀ-Ýa-zà-ÿ'’\-–]+(?:\s+[A-ZÀ-Ýa-zà-ÿ'’\-–]+){0,3}", line)
                and len(line) < 60 and not EMAIL_RE.search(line)):
            name = line
            break
    # Title: next few lines, short, keyword-ish
    for line in lines[1:8]:
        if line != name and len(line) < 80 and not EMAIL_RE.search(line) and not PHONE_RE.search(line):
            title = line
            if not re.match(r"^(summary|profile|about|experience|skills|education):", line, re.I):
                break
    joined = "\n".join(lines)
    email = EMAIL_RE.search(joined)
    phone = PHONE_RE.search(joined)
    urls = URL_RE.findall(joined)
    # Location: "City, Country" pattern among the first lines (handles "a | b | c" contact lines)
    location = ""
    loc_re = re.compile(r"^[A-ZÀ-Ý][\w'’\- ]+,\s*[A-ZÀ-Ý][\w'’\- ]+$")
    for line in lines[:10]:
        segments = [s.strip() for s in line.split("|")]
        for seg in segments:
            if loc_re.match(seg) and not EMAIL_RE.search(seg) and "http" not in seg:
                location = seg
                break
        if location:
            break
    return {
        "name": name,
        "title": title,
        "email": email.group(0) if email else "",
        "phone": phone.group(0).strip() if phone else "",
        "website": (urls[0] if urls else ""),
        "location": location,
        "raw": joined,
    }


def parse_cv(source: str) -> CVData:
    """Parse a CV from a file path (pdf/docx/md/txt) or raw text string."""
    text = source
    if len(source) < 400 and Path(source).exists() and "\n" not in source[:50]:
        # It's a path
        path = Path(source)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif suffix == ".docx":
            import docx
            doc = docx.Document(str(path))
            text = "\n".join(p.text for p in doc.paragraphs)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")

    base = _simple_parse(text)
    sections = _split_sections(text)
    domain, label = detect_domain(text)

    raw_skills = sections.get("skills", "")
    skills = []
    for line in raw_skills.splitlines():
        line = line.lstrip("-•*·,;").strip()
        if not line:
            continue
        if line.count(",") >= 1 and not line.startswith(("C++", "C#")) and "Visual Basic" not in line:
            parts = [p for p in (s.strip() for s in line.split(",")) if p]
            skills.extend(parts[:8])
        else:
            skills.append(line)
    skills = skills[:24]

    HEADER_RE = re.compile(r"^[A-ZÀ-Ý0-9][\w\s'’\-–—&/+,.()%£€:]{2,160}$")
    DATE_RANGE_RE = re.compile(
        r"\(\s*(?:19|20)\d{2}\s*[–—-]\s*(?:(?:19|20)\d{2}|present|présent|now|today|en\s+cours|aujourd)",
        re.IGNORECASE,
    )

    def _bullets(block: str, bullets_are_items: bool = False) -> list[dict]:
        """Parse a section. bullets_are_items=True -> each bullet is its own entry."""
        items: list[dict] = []
        current: dict | None = None
        for raw in block.splitlines():
            line = raw.strip()
            if not line:
                continue
            is_bullet = bool(re.match(r"^[-•*·◦▪]\s", line))
            content = re.sub(r"^[-•*·◦▪]\s*", "", line).strip()
            if not content:
                continue
            if bullets_are_items and is_bullet:
                items.append({"title": content, "details": []})
                continue
            is_entry_header = bool(DATE_RANGE_RE.search(content)) or (
                not is_bullet and len(content) < 120 and HEADER_RE.match(content)
                and not content.endswith(".")
            )
            if is_entry_header:
                if current is not None and (current["title"] or current["details"]):
                    items.append(current)
                current = {"title": content, "details": []}
                continue
            if is_bullet:
                if current is None:
                    current = {"title": content, "details": []}
                else:
                    current["details"].append(content)
                continue
            # plain detail line
            if current is None:
                current = {"title": content[:80], "details": []}
            else:
                current["details"].append(content)
        if current is not None and (current["title"] or current["details"]):
            items.append(current)
        return items

    experience = _bullets(sections.get("experience", ""))
    education = _bullets(sections.get("education", ""))
    projects = _bullets(sections.get("projects", ""), bullets_are_items=True)
    languages = [
        l.strip().lstrip("-•*·,").strip()
        for l in sections.get("languages", "").splitlines()
        if l.strip()
    ]
    if len(languages) == 1 and "," in languages[0]:
        languages = [x.strip() for x in languages[0].split(",") if x.strip()]
    summary = sections.get("summary", "")[:600]

    return CVData(
        name=base["name"],
        title=base["title"],
        email=base["email"],
        phone=base["phone"],
        location=base.get("location", ""),
        website=base["website"],
        summary=summary,
        skills=skills[:20],
        experience=experience[:8],
        education=education[:6],
        projects=projects[:8],
        languages=languages[:8],
        domain=domain,
        domain_label=label,
    )


if __name__ == "__main__":
    import sys
    data = parse_cv(sys.argv[1] if len(sys.argv) > 1 else "samples/example-cv.md")
    print(json.dumps(data.to_dict(), indent=2, ensure_ascii=False))
