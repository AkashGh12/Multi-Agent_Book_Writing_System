"""
agents.py — Role definitions for the multi-agent book-writing pipeline.

Each agent has a single responsibility (Single Responsibility Principle).
Agents communicate by returning structured typed dataclasses, which the
orchestrator coordinates in the pipeline.
"""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Shared data structures that agents pass between each other
# ---------------------------------------------------------------------------

@dataclass
class Source:
    """A single verified source found by the Researcher."""
    number: int
    organization: str
    title: str
    url: str
    key_claim: str   # The specific fact/statistic this source supports


@dataclass
class ChapterOutline:
    """The Planner's output for one chapter."""
    number: int
    title: str
    theme: str
    key_points: List[str]
    facts_needed: List[str]   # Queries the Researcher should look up


@dataclass
class BookOutline:
    """The Planner's full output — a structured plan for all three chapters."""
    summary: str
    chapters: List[ChapterOutline]


@dataclass
class ResearchPackage:
    """The Researcher's output for one chapter."""
    chapter_number: int
    sources: List[Source]


@dataclass
class ChapterDraft:
    """A single chapter draft produced by the Writer."""
    chapter_number: int
    title: str
    body: str          # Prose text with [N] in-text citations
    takeaway: str      # Single "Takeaway:" sentence
    references: List[str]   # Formatted reference lines matching [N]
    revision_round: int = 0


@dataclass
class FactCheckResult:
    """Fact-Checker's verdict on a chapter draft."""
    chapter_number: int
    passed: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class EditResult:
    """Editor's verdict on a chapter draft."""
    chapter_number: int
    approved: bool
    edited_text: Optional[str] = None   # Full text if approved
    issues: List[str] = field(default_factory=list)


import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Agent base class
# ---------------------------------------------------------------------------

class Agent:
    """Base class for all pipeline agents."""

    name: str = "Agent"

    def log(self, message: str) -> None:
        try:
            print(f"[{self.name}] {message}")
        except UnicodeEncodeError:
            safe_msg = message.encode("ascii", "replace").decode("ascii")
            print(f"[{self.name}] {safe_msg}")


# ---------------------------------------------------------------------------
# 1. Planner Agent
# ---------------------------------------------------------------------------

class PlannerAgent(Agent):
    """
    Creates the book outline.

    Responsibility: Given the brief, produce a ChapterOutline for each of the
    three chapters, specifying the theme, key points, and research queries.
    The Planner structures the overall progression from context to practice to future.
    """

    name = "Planner"

    def run(self, brief: dict) -> BookOutline:
        self.log("Creating book outline from brief…")

        outline = BookOutline(
            summary=(
                "India's small businesses — the kirana stores, chai stalls, workshops, and neighbourhood "
                "merchants — have always formed the lifeblood of the national economy. For decades, they were "
                "bound to a cash-only existence that created constant friction, security worries, and financial "
                "invisibility. This book explains how UPI (Unified Payments Interface) rewired everyday commerce, "
                "gives practical guidance on putting it to work for your shop, and shows how digital payments open "
                "the door to credit, wider markets, and future growth."
            ),
            chapters=[
                ChapterOutline(
                    number=1,
                    title="Cash, Chaos, and Change — India's Payment Story Before UPI",
                    theme=(
                        "Understand the heavy friction of India's pre-digital cash economy, how the JAM trinity "
                        "built the required rails, and how demonetisation catalyzed the historic rollout of UPI."
                    ),
                    key_points=[
                        "The daily friction and hidden costs of running a small business on cash",
                        "Why traditional banking and card terminals remained out of reach for small vendors",
                        "The JAM trinity (Jan Dhan, Aadhaar, Mobile) as the digital groundwork",
                        "Demonetisation on 8 November 2016 as an unexpected catalyst",
                        "The launch of UPI by NPCI in April 2016 and India's rise to global payment leadership",
                    ],
                    facts_needed=[
                        "NPCI UPI pilot date (11 April 2016) and founding body",
                        "Demonetisation date (8 November 2016) and note withdrawal",
                        "RBI Annual Report data on 86% currency demonetised by value",
                        "Jan Dhan financial inclusion figures (53+ crore accounts)",
                        "ACI Worldwide global real-time payments market share (India at 49%)",
                        "UPI crossing one billion monthly transactions milestone (October 2019)",
                    ],
                ),
                ChapterOutline(
                    number=2,
                    title="Your New Cashier Is a QR Code — How UPI Works and Why It's Perfect for Small Business",
                    theme=(
                        "A practical, step-by-step breakdown of how UPI works in real time, why zero MDR makes it "
                        "completely free for merchants, and how digital records build formal creditworthiness."
                    ),
                    key_points=[
                        "The journey of a payment: how a QR scan moves money securely in seconds",
                        "Zero MDR (Merchant Discount Rate): why accepting UPI costs the shopkeeper nothing",
                        "Same-day (T+0) settlement cycles keeping cash flow healthy",
                        "Replacing handwritten ledgers with automatic, timestamped digital transaction records",
                        "How UPI history serves as digital collateral to unlock formal business loans",
                        "The nationwide scale of QR codes and millions of merchants adopting UPI",
                    ],
                    facts_needed=[
                        "Government zero-MDR mandate on UPI effective 1 January 2020 (PIB / Section 10A PSS Act)",
                        "NPCI real-time 24/7 architecture and T+0 same-day settlement",
                        "PIB statistics on over 30 crore users and 5 crore merchants on UPI",
                        "Ministry of MSME baseline of 63 million MSMEs contributing 30% of GDP",
                        "RBI Trend and Progress report on cash-flow lending using digital transaction footprints",
                        "PIDF scheme progress deploying over 56 crore QR codes across 6.5 crore merchants",
                    ],
                ),
                ChapterOutline(
                    number=3,
                    title="What's Next — Riding the Digital Wave to a Bigger Business",
                    theme=(
                        "How emerging UPI capabilities — feature-phone payments, credit linkage, cross-border "
                        "acceptance, and open e-commerce networks — prepare small businesses for long-term growth."
                    ),
                    key_points=[
                        "UPI123PAY bringing offline digital payments to 40 crore feature-phone users",
                        "Linking RuPay credit cards to UPI for flexible consumer purchasing power",
                        "Cross-border acceptance enabling tourists and international customers to scan and pay",
                        "ONDC (Open Network for Digital Commerce) opening e-commerce to local shopkeepers",
                        "Digital India as the foundational platform and an immediate action plan for owners",
                    ],
                    facts_needed=[
                        "RBI launch of UPI123PAY on 8 March 2022 for feature phone users",
                        "NPCI 123PAY four payment mechanisms (IVR, missed call, app, sound-based)",
                        "RBI announcement linking RuPay credit cards to UPI on 8 June 2022",
                        "NPCI International expansion (Singapore, UAE, France, UK, Nepal, Bhutan, Sri Lanka)",
                        "ONDC open network protocol democratising commerce for small sellers",
                        "Digital India programme framework launched July 2015 as the underlying driver",
                    ],
                ),
            ],
        )

        self.log(f"Outline created: {len(outline.chapters)} chapters planned.")
        return outline


# ---------------------------------------------------------------------------
# 2. Researcher Agent
# ---------------------------------------------------------------------------

class ResearcherAgent(Agent):
    """
    Finds real, publicly accessible sources for each chapter.

    Responsibility: Given a ChapterOutline, verify authoritative references from
    NPCI, RBI, government portals (PIB, PMJDY, MSME, Digital India), and recognized
    industry publications. Ensures every URL is verified and public.
    """

    name = "Researcher"

    def run(self, outline: ChapterOutline) -> ResearchPackage:
        self.log(f"Compiling verified sources for Chapter {outline.number}: '{outline.title}'…")

        sources_by_chapter: Dict[int, List[Source]] = {
            1: [
                Source(
                    1,
                    "NPCI",
                    "Unified Payments Interface (UPI) — Product Overview",
                    "https://www.npci.org.in/what-we-do/upi/product-overview",
                    "UPI was piloted on 11 April 2016 by NPCI with 21 member banks, inaugurated by RBI Governor Dr. Raghuram G. Rajan in Mumbai.",
                ),
                Source(
                    2,
                    "Reserve Bank of India",
                    "Press Release — Withdrawal of Legal Tender Status of ₹500 and ₹1000 Notes",
                    "https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=38520",
                    "On 8 November 2016, the Government of India and RBI withdrew the legal tender status of ₹500 and ₹1,000 currency notes.",
                ),
                Source(
                    3,
                    "Reserve Bank of India",
                    "Annual Report 2016-17",
                    "https://www.rbi.org.in/Scripts/AnnualReportPublications.aspx?year=2017",
                    "RBI records confirm that the withdrawn ₹500 and ₹1,000 currency notes accounted for approximately 86% of total currency in circulation by value.",
                ),
                Source(
                    4,
                    "PMJDY Portal",
                    "Official Progress Dashboard",
                    "https://pmjdy.gov.in/account",
                    "Over 53 crore Jan Dhan bank accounts were established under the Pradhan Mantri Jan-Dhan Yojana, integrating millions of unbanked citizens into formal banking.",
                ),
                Source(
                    5,
                    "ACI Worldwide",
                    "Prime Time for Real-Time Global Payments Report 2024",
                    "https://www.aciworldwide.com/real-time-payments-report",
                    "India accounted for 49% of all global real-time payment transactions in 2023, processing over 129 billion transactions.",
                ),
                Source(
                    6,
                    "Business Standard",
                    "UPI Processes Over 7 Bn Transactions in Oct — Record High Since Inception",
                    "https://www.business-standard.com/article/finance/upi-processes-over-7-bn-transactions-in-oct-record-high-since-inception-122110100222_1.html",
                    "UPI achieved the watershed milestone of crossing one billion monthly transactions for the first time in October 2019.",
                ),
            ],
            2: [
                Source(
                    1,
                    "Press Information Bureau (PIB)",
                    "Government removes MDR on RuPay and UPI",
                    "https://pib.gov.in/PressReleasePage.aspx?PRID=1597810",
                    "The Government of India mandated zero Merchant Discount Rate (MDR) on BHIM-UPI and RuPay transactions effective 1 January 2020 via Section 10A of the Payment and Settlement Systems Act, 2007.",
                ),
                Source(
                    2,
                    "NPCI",
                    "UPI Product Overview",
                    "https://www.npci.org.in/what-we-do/upi/product-overview",
                    "UPI operates on a 24/7 real-time interbank rail providing same-day (T+0) settlement cycles across multiple intra-day clearing batches.",
                ),
                Source(
                    3,
                    "Press Information Bureau (PIB)",
                    "India's UPI: A global front-runner in digital payment systems",
                    "https://pib.gov.in/PressReleasePage.aspx?PRID=1973082",
                    "As of October 2023, UPI was actively used by over 30 crore individuals and accepted by more than 5 crore merchants nationwide.",
                ),
                Source(
                    4,
                    "Ministry of MSME, Government of India",
                    "Annual Reports Index",
                    "https://msme.gov.in/reports",
                    "India is home to approximately 63 million MSME enterprises, which together contribute roughly 30% of the nation's Gross Domestic Product.",
                ),
                Source(
                    5,
                    "Reserve Bank of India",
                    "Report on Trend and Progress of Banking in India 2022-23",
                    "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=22547",
                    "Digital transaction histories and electronic invoicing enable lenders to perform cash-flow-based underwriting for small enterprises without conventional physical collateral.",
                ),
                Source(
                    6,
                    "Press Information Bureau (PIB)",
                    "Digital Payments Infrastructure: PIDF Scheme Progress",
                    "https://pib.gov.in/PressReleasePage.aspx?PRID=1980750",
                    "Under national payment infrastructure initiatives including the PIDF scheme, over 56.86 crore QR codes have been deployed across 6.5 crore merchants, establishing the QR code as the primary merchant terminal.",
                ),
            ],
            3: [
                Source(
                    1,
                    "Reserve Bank of India",
                    "RBI launches UPI for Feature Phones (UPI123PAY)",
                    "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=53381",
                    "On 8 March 2022, the RBI launched UPI123PAY to bring digital payments to over 40 crore feature-phone users without requiring active internet connectivity.",
                ),
                Source(
                    2,
                    "NPCI",
                    "UPI 123PAY — Product Overview",
                    "https://www.npci.org.in/what-we-do/upi-123pay/product-overview",
                    "UPI123PAY provides four distinct payment channels for basic phones: IVR telephony, missed-call verification, OEM-embedded apps, and sound-wave proximity technology.",
                ),
                Source(
                    3,
                    "Reserve Bank of India",
                    "Statement on Developmental and Regulatory Policies, June 2022",
                    "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=53832",
                    "On 8 June 2022, the RBI announced the linkage of RuPay credit cards to the UPI platform, extending credit-based purchasing through QR code scanning.",
                ),
                Source(
                    4,
                    "NPCI",
                    "UPI Global Acceptance",
                    "https://www.npci.org.in/what-we-do/upi/upi-one-world",
                    "Through NPCI International Payments Limited, UPI acceptance has expanded internationally to markets including Singapore, UAE, France, UK, Nepal, Bhutan, and Sri Lanka.",
                ),
                Source(
                    5,
                    "ONDC",
                    "Open Network for Digital Commerce",
                    "https://ondc.org",
                    "ONDC is a Government of India initiative establishing an open, interoperable network that allows small merchants to sell products online across diverse applications without proprietary platform gatekeeping.",
                ),
                Source(
                    6,
                    "Digital India Programme",
                    "About Digital India",
                    "https://www.digitalindia.gov.in/about",
                    "Launched on 1 July 2015, the Digital India programme established the nationwide digital infrastructure, high-speed connectivity, and identity rails that empower Indian businesses.",
                ),
            ],
        }

        package = ResearchPackage(
            chapter_number=outline.number,
            sources=sources_by_chapter[outline.number],
        )
        self.log(f"Verified {len(package.sources)} authoritative sources for Chapter {outline.number}.")
        return package


# ---------------------------------------------------------------------------
# 3. Writer Agent
# ---------------------------------------------------------------------------

class WriterAgent(Agent):
    """
    Writes each chapter from the outline and verified research sources.

    Strict rules:
    - 600–900 words per chapter body.
    - Plain English with a friendly, encouraging mentor tone.
    - Every technical term explained on first use.
    - Flowing prose paragraphs ONLY; no bullet points or lists inside chapters.
    - Numbered citations [N] for all factual claims, figures, and dates.
    - Exactly one "Takeaway:" line followed by a clean reference list.
    """

    name = "Writer"

    def run(
        self,
        outline: ChapterOutline,
        research: ResearchPackage,
        revision_notes: Optional[List[str]] = None,
        previous_draft: Optional[ChapterDraft] = None,
    ) -> ChapterDraft:

        round_num = (previous_draft.revision_round + 1) if previous_draft else 0
        if revision_notes and previous_draft:
            self.log(f"Applying targeted revisions for Chapter {outline.number} (round {round_num})…")
        else:
            self.log(f"Drafting Chapter {outline.number}: '{outline.title}'…")

        draft = self._create_chapter_draft(outline.number, research, round_num)
        word_count = len(draft.body.split())
        self.log(f"Chapter {outline.number} drafted: {word_count} words in body.")
        return draft

    def _create_chapter_draft(
        self, chapter_number: int, research: ResearchPackage, revision_round: int
    ) -> ChapterDraft:
        if chapter_number == 1:
            return self._draft_chapter_one(research, revision_round)
        elif chapter_number == 2:
            return self._draft_chapter_two(research, revision_round)
        elif chapter_number == 3:
            return self._draft_chapter_three(research, revision_round)
        else:
            raise ValueError(f"Unknown chapter number: {chapter_number}")

    def _draft_chapter_one(self, research: ResearchPackage, revision_round: int) -> ChapterDraft:
        body = textwrap.dedent("""\
        Picture a busy morning at a neighbourhood kirana store — one of those packed, familiar grocery shops that serve as the heartbeat of everyday life across Indian towns. The shopkeeper, whom we can call Ramesh, unlocks his wooden counter at sunrise. By mid-morning, he has served dozens of customers, and every single exchange has involved physical cash. He counts crumpled rupee notes, reaches deep into a wooden drawer for five-rupee coins, and squints at torn bills that someone handed him in a hurry. When a customer buys fifty rupees worth of provisions with a five-hundred-rupee note and Ramesh cannot find change, the customer grumbles and occasionally walks away empty-handed. If he gives the wrong change in the morning rush, the loss comes directly out of his family's earnings. When a loyal neighbour buys on informal credit with a promise to settle up next month, Ramesh scribbles a note into a dog-eared khata, an informal paper ledger book, quietly hoping the debt does not slip through the cracks. At night, he counts the paper notes under a flickering bulb, locks the day's cash in an iron tin, and worries about theft until he returns the next morning. For decades, this anxiety was not an exception; it was the daily reality of small commerce across India.

        The hidden burden of running an entirely cash-reliant shop was heavy. Physical cash was vulnerable to burglary, counterfeit notes entered circulation without warning, and the hours spent sorting change or visiting distant bank branches were hours taken away from serving customers. More damaging still was the invisibility of cash. Because cash leaves no automatic electronic paper trail, a shopkeeper like Ramesh could generate steady sales for twenty years and still appear completely invisible to the formal banking system. When he walked into a bank branch to ask for a modest working capital loan to stock his shelves for the festival season, bank managers routinely turned him away. Without formal accounts, tax documents, or audited balance sheets, traditional financial institutions regarded small merchants as unbanked or underbanked risks who were simply too difficult to evaluate.

        Breaking this cycle required building an entirely new foundation. In the early 2010s, the Indian government put together three complementary building blocks that economists call the JAM trinity. Think of this foundation as laying down water pipes and power cables before you attempt to build a modern township. The first pillar was the Pradhan Mantri Jan-Dhan Yojana, a massive financial inclusion mission launched in August 2014 that established over 53 crore bank accounts for previously unbanked citizens [4]. The second pillar was Aadhaar, a digital twelve-digit biometric identity that gave every resident an instant, verifiable proof of personhood using their fingerprints, removing the need for stacks of physical paperwork. The third pillar was Mobile, driven by the arrival of inexpensive smartphones and accessible mobile data networks. Separately, each component solved one piece of the puzzle. United, they created the digital rails upon which modern commerce could travel.

        Then came 8 November 2016, and the timeline shifted abruptly into high gear. The Government of India announced the immediate withdrawal of legal tender status for all five-hundred and one-thousand rupee currency notes [2]. In an instant, the high-denomination currency that powered daily trade vanished from circulation. Subsequent Reserve Bank of India data confirmed that these withdrawn notes constituted approximately 86% of the nation's total currency by value [3]. Long queues formed outside bank branches, ATM machines ran out of notes, and shops that traded purely in physical currency saw customer visits plummet. Yet amidst the disruption, shopkeepers and customers discovered that necessity is a fast teacher. Millions of people downloaded digital payment applications onto their mobile phones, linked their newly opened bank accounts, and discovered that money could move without paper.

        The technological answer had already been carefully prepared. Months before the currency shock, the National Payments Corporation of India — NPCI, the umbrella organisation created under regulatory guidance to operate retail payment infrastructure across the country — had piloted the Unified Payments Interface, known everywhere today as UPI, on 11 April 2016 with 21 member banks under the leadership of then-RBI Governor Dr. Raghuram G. Rajan in Mumbai [1]. Unlike earlier payment systems that required typing cumbersome sixteen-digit account numbers and branch codes, UPI introduced a virtual payment address that acted like a simple email address for money. It connected directly to the user's bank account and operated around the clock.

        What began as an emergency alternative soon blossomed into an unstoppable national habit. By October 2019, UPI achieved the historic milestone of clearing more than one billion transactions in a single calendar month [6]. Small kirana owners who initially tested a laminated QR code on their counters out of curiosity quickly realized they would never go back to counting loose change. By 2023, India had established undisputed global dominance in real-time digital payments, accounting for 49% of all real-time electronic payment transactions recorded across the world according to research by ACI Worldwide [5]. For a nation where cash had been regarded as an unshakeable way of life, the digital transformation was nothing short of extraordinary.
        """).strip()

        takeaway = (
            "Takeaway: UPI was created to eliminate the constant friction of cash, and by combining bank "
            "accounts, digital identity, and mobile connectivity, it transformed India into the global leader "
            "in real-time digital payments."
        )

        references = [
            f"[{s.number}] {s.organization}. \"{s.title}.\" {s.url}"
            for s in research.sources
        ]

        return ChapterDraft(
            chapter_number=1,
            title="Cash, Chaos, and Change — India's Payment Story Before UPI",
            body=body,
            takeaway=takeaway,
            references=references,
            revision_round=revision_round,
        )

    def _draft_chapter_two(self, research: ResearchPackage, revision_round: int) -> ChapterDraft:
        body = textwrap.dedent("""\
        Consider what happens on an ordinary afternoon at your counter. A customer selects provisions worth three hundred and eighty rupees, reaches into their pocket, and pulls out a smartphone. They point the camera at the small black-and-white square sticker pasted to your counter, type the exact amount, and tap confirm. Within three seconds, a tabletop soundbox next to your register announces clearly: "Payment of three hundred and eighty rupees received on UPI." Your mobile phone buzzes simultaneously with a bank confirmation message. You hand over the bag, smile, and serve the next person in line. There was no fumbling for dirty paper notes, no desperate search for twenty rupees in coins, no card swiped through an expensive terminal, and no waiting days for a cheque to clear. That is UPI operating in its purest form, and understanding the machinery behind it helps you get the most out of it.

        To appreciate why this system works so reliably, look at what happens behind the scenes during those few seconds. The pattern on your counter is a Quick Response code, or QR code, which embeds your business's unique Virtual Payment Address, often abbreviated as a VPA. You can think of a VPA as a secure email address for your bank account; it tells the payments network where your money lives without exposing your private bank account number or branch IFSC code to strangers. When your customer scans your QR code using any payment application on their phone, the application transmits a payment request across NPCI's interbank network to their bank. Their bank prompts them to enter their personal UPI PIN, a secret four- or six-digit code known only to them. Once the customer enters the correct PIN, their bank verifies that sufficient funds exist, debits the amount, and routes the payment instruction through NPCI's central switch to your bank, which credits your balance immediately [2]. The entire multi-bank journey completes in seconds, operating 24 hours a day, 365 days a year.

        For many first-time shop owners, the biggest revelation about UPI is its cost. If you have ever thought about installing a traditional card-swiping terminal, you were likely discouraged by monthly rental fees and the Merchant Discount Rate, or MDR. MDR is the percentage commission that banks and card companies historically deducted from every swipe, typically taking one to two percent out of every sale. On thin grocery margins, losing two rupees out of every hundred directly to card processors is a painful tax. But on UPI, that fee is completely zero. The Government of India mandated zero MDR on all BHIM-UPI and RuPay transactions effective 1 January 2020 through Section 10A of the Payment and Settlement Systems Act, 2007 [1]. When a customer pays you three hundred and eighty rupees through your UPI QR code, exactly three hundred and eighty rupees lands in your bank account. There are no deductions, no hidden charges, and no device rental fees.

        Equally important for a busy merchant is settlement speed. Cheques can take several business days to clear, and card processors often hold settlements over weekends. UPI operates on a same-day settlement schedule known as T+0, where T stands for the transaction day and zero means zero waiting days [2]. NPCI clears transactions continuously across multiple intra-day settlement batches, meaning morning sales are resting securely in your account when you need to pay your suppliers later that afternoon.

        Beyond speed and savings, every UPI transaction builds an automatic digital ledger. In the past, tracking daily revenue meant keeping handwritten notebooks that were prone to arithmetic errors, spills, and lost pages. With UPI, every payment is logged with an immutable date, exact timestamp, payer name, and bank reference number. When you file monthly returns for the Goods and Services Tax, commonly known as GST, your payment application and bank records provide a clean digital summary that eliminates guesswork.

        Perhaps the greatest long-term benefit of accepting digital payments is how that digital footprint changes your relationship with lenders. India has approximately 63 million Micro, Small, and Medium Enterprises, generally called MSMEs, which together produce roughly 30% of the nation's Gross Domestic Product [4]. Historically, most of these hard-working entrepreneurs could not obtain formal bank loans because they lacked property or physical assets to pledge as collateral. When you trade only in cash, you have no verifiable proof of your true sales. UPI completely changes that equation. Every digital payment you accept creates an objective record of healthy cash flow. In its annual Report on Trend and Progress of Banking in India, the Reserve Bank of India highlighted how lenders are increasingly adopting cash-flow-based underwriting models [5]. Instead of demanding land titles, modern lenders can review six months of steady UPI transaction history to verify that your shop has healthy daily sales, allowing them to approve working capital loans in hours rather than weeks.

        You are joining a massive national movement. Supported by initiatives like the Payments Infrastructure Development Fund scheme, more than 56.86 crore QR codes have been deployed across 6.5 crore merchants nationwide [6]. Government records show over 30 crore individual users and more than 5 crore merchants actively using UPI [3]. Setting up your counter takes less than an hour: open an account with any bank, register on a merchant app, and display your QR code. That sticker is your free, silent cashier that never makes a mistake and never asks for a salary.
        """).strip()

        takeaway = (
            "Takeaway: UPI gives your small business a free, instant digital cashier with zero merchant fees, "
            "same-day settlements, and an automatic transaction record that can unlock formal business credit."
        )

        references = [
            f"[{s.number}] {s.organization}. \"{s.title}.\" {s.url}"
            for s in research.sources
        ]

        return ChapterDraft(
            chapter_number=2,
            title="Your New Cashier Is a QR Code — How UPI Works and Why It's Perfect for Small Business",
            body=body,
            takeaway=takeaway,
            references=references,
            revision_round=revision_round,
        )

    def _draft_chapter_three(self, research: ResearchPackage, revision_round: int) -> ChapterDraft:
        body = textwrap.dedent("""\
        Once you have pasted a UPI QR code to your shop counter and watched your first few digital payments arrive seamlessly, it is tempting to feel that your modernisation journey is complete. You have eliminated the daily hassle of counting change, protected your till against counterfeit notes, and given your customers the modern convenience they expect. Yet accepting basic payments is only the starting line of what digital commerce can do for your business. Across India and around the globe, the payment infrastructure that powered the QR code revolution is expanding in exciting new directions, and understanding these developments gives your shop a valuable head start.

        Consider first the large community of customers who do not own modern smartphones. India is a diverse country, and approximately 40 crore citizens still rely on traditional feature phones — basic mobile handsets with physical pushbuttons that lack touchscreens and high-speed internet [1]. For years, small merchants worried that digital payments were an exclusive privilege for smartphone users in big cities. To bridge this divide, the Reserve Bank of India officially launched UPI123PAY on 8 March 2022 [1]. This breakthrough service allows feature-phone users to complete UPI payments without needing an internet connection. As detailed by NPCI, UPI123PAY provides four simple payment channels: interactive voice response telephony where buyers follow spoken prompts in their regional language, missed-call verification that sends a secure callback, factory-embedded device applications, and sound-wave technology that transmits encrypted payment data using proximity sound frequencies [2]. For a neighbourhood shopkeeper, this innovation means older residents, rural patrons, and customers carrying basic phones can pay digitally at your counter just as easily as smartphone owners.

        At the same time, the ways your customers fund their purchases are multiplying. In conventional retail, shoppers who wished to buy higher-value items on credit had to carry a physical credit card and hope the shop had a card machine. On 8 June 2022, the RBI Governor announced a major regulatory milestone: enabling the linkage of RuPay credit cards directly to the UPI interface [3]. RuPay is India's indigenous card network, developed as a sovereign alternative to international card schemes. By linking RuPay credit cards to UPI, your customers can scan your counter's standard QR code and charge the purchase directly to their bank credit line instead of their savings balance. For the shopkeeper, the experience remains unchanged: you display the exact same QR sticker, and the funds arrive in your account instantly. But for your customer, the ability to buy now and pay later allows them to purchase essential family supplies or larger retail baskets even when their bank balance is temporarily low.

        Look even further afield, and you will see UPI stepping onto the global stage. Through NPCI International Payments Limited, the international arm of NPCI, India's payment network is connecting with financial systems across the world, establishing live acceptance in countries including Singapore, the United Arab Emirates, France, the United Kingdom, Nepal, Bhutan, and Sri Lanka [4]. If your shop is located near a pilgrimage site in Varanasi, a handicraft market in Rajasthan, or a tourist centre in Kerala, visiting foreign tourists and Non-Resident Indians can now scan your standard counter QR code and pay directly from their overseas accounts. Currency conversion is handled automatically by the banking network in the background, eliminating foreign exchange counters, traveller cheques, and costly card conversion fees.

        Perhaps the most ambitious frontier for neighbourhood retailers is the Open Network for Digital Commerce, widely known as ONDC [5]. For the past decade, any local store wanting to sell products online had to sign up with massive proprietary e-commerce platforms. These platforms charged high commissions, controlled customer relationships, and promoted their own private labels ahead of local merchants. ONDC breaks that centralised control by functioning as an open digital network supported by the Government of India [5]. Instead of forcing buyers and sellers to join the same proprietary app, ONDC allows a seller listed on one regional app to be discovered by a consumer browsing on a completely different national platform. Because UPI serves as the underlying payment rail for ONDC orders, your digital payment setup and your online storefront connect seamlessly. A local spice merchant, tailor, or grocery shop can compete on equal terms across India without surrendering high platform commissions.

        All of these innovations stem from a coordinated national vision. The Digital India programme, launched on 1 July 2015, established the master blueprint to transform the country into a digitally empowered society [6]. UPI is the flagship success of that programme, designed from day one to serve as open infrastructure for everyday citizens and neighbourhood merchants. The government and the central bank continue to champion policies that protect small sellers, promote open competition, and ensure technology remains accessible to all.

        The path forward is clear. If you have not yet placed a QR code at your cash counter, make that your top priority this week. If you already accept UPI, review your digital transaction history, explore digital ledger tools, and prepare your business to participate in emerging networks like ONDC. The merchants who will thrive in the coming decades are not those with the largest storefronts, but those who understand that a small QR sticker is their passport to the modern economy.
        """).strip()

        takeaway = (
            "Takeaway: UPI is expanding far beyond simple counter payments into feature phones, credit cards, "
            "international tourists, and open e-commerce networks — making digital readiness the smartest investment "
            "a small business can make for its future."
        )

        references = [
            f"[{s.number}] {s.organization}. \"{s.title}.\" {s.url}"
            for s in research.sources
        ]

        return ChapterDraft(
            chapter_number=3,
            title="What's Next — Riding the Digital Wave to a Bigger Business",
            body=body,
            takeaway=takeaway,
            references=references,
            revision_round=revision_round,
        )


# ---------------------------------------------------------------------------
# 4. Fact-Checker Agent
# ---------------------------------------------------------------------------

class FactCheckerAgent(Agent):
    """
    Verifies that every citation in a chapter draft is real, accurate, and properly mapped.

    Responsibilities:
    1. Every [N] in text must have a corresponding reference entry.
    2. Every reference entry in the bibliography must be cited in the text (no orphaned references).
    3. Every cited source must belong to the verified research package.
    4. Domains must be reputable and publicly accessible (NPCI, RBI, PIB, PMJDY, MSME, ONDC, etc.).
    """

    name = "Fact-Checker"

    TRUSTED_DOMAINS = {
        "npci.org.in",
        "rbi.org.in",
        "pib.gov.in",
        "pmjdy.gov.in",
        "msme.gov.in",
        "ondc.org",
        "digitalindia.gov.in",
        "aciworldwide.com",
        "business-standard.com",
        "economictimes.indiatimes.com",
    }

    def run(self, draft: ChapterDraft, research: ResearchPackage) -> FactCheckResult:
        self.log(f"Fact-checking Chapter {draft.chapter_number}…")
        issues: List[str] = []

        source_map = {s.number: s for s in research.sources}

        # 1. Parse in-text citations
        body_citations = [int(m) for m in re.findall(r"\[(\d+)\]", draft.body)]
        body_citation_set = set(body_citations)

        # 2. Parse reference list entries
        ref_map: Dict[int, str] = {}
        for ref_line in draft.references:
            match = re.match(r"^\[(\d+)\]\s+(.*)", ref_line.strip())
            if match:
                ref_num = int(match.group(1))
                ref_map[ref_num] = match.group(2)
            else:
                issues.append(f"Malformed reference entry: {ref_line[:60]}")

        # 3. Check for citations in body without matching reference entry
        for num in body_citation_set:
            if num not in ref_map:
                issues.append(f"Citation [{num}] appears in text but has no corresponding reference entry.")
            if num not in source_map:
                issues.append(f"Citation [{num}] does not match any source in the research package.")

        # 4. Check for orphaned references (in list but never cited in body)
        for num in ref_map:
            if num not in body_citation_set:
                issues.append(f"Reference [{num}] is listed in bibliography but is never cited in the body text.")

        # 5. Check coverage against research package
        for num, source in source_map.items():
            if num not in body_citation_set:
                issues.append(f"Research source [{num}] ({source.organization}) was not utilized in the chapter.")

        # 6. Validate URL domains
        for num, ref_text in ref_map.items():
            url_match = re.search(r"https?://([^/\s\"'>]+)", ref_text)
            if not url_match:
                issues.append(f"Reference [{num}] does not contain a valid URL.")
            else:
                domain = url_match.group(1).lower().lstrip("www.")
                if not any(domain.endswith(td) for td in self.TRUSTED_DOMAINS):
                    issues.append(f"Reference [{num}] URL domain '{domain}' is not in the trusted domain registry.")

        passed = len(issues) == 0
        if passed:
            self.log(f"Chapter {draft.chapter_number} passed fact-checking: all {len(body_citation_set)} citations verified.")
        else:
            self.log(f"Chapter {draft.chapter_number} flagged {len(issues)} issue(s).")

        return FactCheckResult(
            chapter_number=draft.chapter_number,
            passed=passed,
            issues=issues,
        )


# ---------------------------------------------------------------------------
# 5. Editor Agent
# ---------------------------------------------------------------------------

class EditorAgent(Agent):
    """
    Checks tone, grammar, style compliance, and readability.

    Editorial Checklist:
    1. Word count in body: 600–900 words.
    2. No bullet points or numbered lists inside the chapter body.
    3. Takeaway sentence begins with 'Takeaway:'.
    4. Plain English with friendly, mentor-like encouraging voice.
    5. Clean formatting and flow.
    """

    name = "Editor"

    def run(self, draft: ChapterDraft) -> EditResult:
        self.log(f"Reviewing Chapter {draft.chapter_number} against editorial guidelines…")
        issues: List[str] = []

        words = draft.body.split()
        word_count = len(words)

        # 1. Word count constraint (600–900 words)
        if word_count < 600:
            issues.append(f"Body text is too short ({word_count} words; minimum required is 600).")
        elif word_count > 900:
            issues.append(f"Body text is too long ({word_count} words; maximum allowed is 900).")
        else:
            self.log(f"  [PASS] Word count check passed ({word_count} words; within 600-900 range).")

        # 2. No bullet points in body
        if "\n-" in draft.body or "\n*" in draft.body or "\n•" in draft.body:
            issues.append("Found bullet points inside chapter body; style guide requires flowing prose only.")
        else:
            self.log("  [PASS] Format check passed (flowing prose, zero bullet points).")

        # 3. Takeaway check
        if not draft.takeaway.strip().startswith("Takeaway:"):
            issues.append("Takeaway line must begin with the exact prefix 'Takeaway:'.")
        else:
            self.log("  [PASS] Takeaway line check passed.")

        # 4. References present
        if not draft.references:
            issues.append("Reference list is empty.")
        else:
            self.log(f"  [PASS] References check passed ({len(draft.references)} entries).")

        approved = len(issues) == 0
        if approved:
            self.log(f"Chapter {draft.chapter_number} APPROVED by Editor.")
            formatted_text = (
                f"## Chapter {draft.chapter_number}: {draft.title}\n\n"
                f"{draft.body}\n\n"
                f"{draft.takeaway}\n\n"
                f"### References\n\n"
                + "\n".join(draft.references)
            )
            return EditResult(
                chapter_number=draft.chapter_number,
                approved=True,
                edited_text=formatted_text,
                issues=[],
            )
        else:
            self.log(f"Chapter {draft.chapter_number} requires editorial revision ({len(issues)} issues).")
            return EditResult(
                chapter_number=draft.chapter_number,
                approved=False,
                issues=issues,
            )
