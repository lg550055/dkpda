import hashlib
from sqlalchemy import select
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from bkend import models
from bkend.schemas import ArticleCreate, Category
from bkend.crud import create_user, get_user_by_email, create_article, get_articles_with_votes



PWD_CONTEXT = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


SEED_ARTICLES = [
    ArticleCreate(
        title="Government Shutdown Enters Third Week; No One Notices",
        content=(
            "WASHINGTON, D.C. — The federal government entered its third week of a complete "
            "shutdown Monday, and according to a Gallup poll conducted yesterday, not a single "
            "American has noticed.\n\n"
            "\"The potholes are the same size, the DMV still takes four hours, and my congressman "
            "still hasn't returned my email from 2019,\" said Rita Combs, 58, of Dayton, Ohio. "
            "\"What exactly changed?\"\n\n"
            "Dr. Helen Park of Georgetown's Center for Public Futility confirmed that all "
            "measurable metrics of federal performance have remained \"statistically identical\" "
            "to pre-shutdown levels. \"If anything, national parks are slightly cleaner,\" "
            "she added. \"Turns out the biggest threat to public lands was the National Park "
            "Service.\" Congress has scheduled an emergency session to address the crisis but "
            "cannot agree on which day of the week it is."
        ),
        image_url="./media/gvmtshtdwn.webp",
        category=Category.GRAFT,
    ),
    ArticleCreate(
        title="Crypto Bros Purchase Island Nation, Collapse Government in Record 72 Hours",
        content=(
            "MIAMI — A consortium of cryptocurrency billionaires purchased the Pacific island "
            "nation of Tavulea on Tuesday to establish a blockchain-based libertarian paradise. "
            "The government collapsed by Friday.\n\n"
            "\"We all agreed the old system is broken,\" explained co-founder Chad Ledger from "
            "his rented yacht. \"Kyle wants proof-of-stake voting. Braden insists on a DAO-based "
            "judiciary. And someone named @CryptoViking69 keeps proposing trial by combat.\"\n\n"
            "The island's 300 residents expressed relief. \"They offered us forty million dollars "
            "in a currency that lost half its value during the sales pitch,\" said village elder "
            "Tui Manu. At press time, the consortium had pivoted to a floating city, which "
            "maritime engineers say will sink both literally and financially within one fiscal quarter."
        ),
        image_url="./media/crypto-moguls.webp",
        category=Category.GRIFT,
    ),
    ArticleCreate(
        title="Milei Announces 'Freedom-Compatible Subsidies,' Dares Economists to Define the Word 'Free'",
        content=(
            "BUENOS AIRES — Argentine President Javier Milei held an impassioned press conference "
            "Thursday praising the invisible hand of the free market while simultaneously announcing "
            "exchange rate controls, export restrictions, and what he called \"freedom-compatible "
            "subsidies.\"\n\n"
            "\"Free markets are the only path to prosperity,\" Milei said, slamming a copy of "
            "Hayek's *The Road to Serfdom* on the podium. \"However, Argentina's markets require "
            "a brief period of government captivity in order to become free. It's like a butterfly. "
            "You must trap it in a jar first.\"\n\n"
            "\"That's not how butterflies work,\" said Dr. Sofia Herrera of the University of Buenos "
            "Aires. \"And it's definitely not how markets work.\" The IMF, which recently approved "
            "a $20 billion package for Argentina, released a two-word statement: \"We know.\""
        ),
        image_url="./media/milei.jpeg",
        category=Category.CRONY,
    ),
    ArticleCreate(
        title="Historic Peace Deal Signed by Two Nations Who Did Not Read It",
        content=(
            "GENEVA — Two nations locked in a decades-long territorial dispute signed a 400-page "
            "peace agreement Wednesday that neither side's leadership has actually read.\n\n"
            "\"Both parties have agreed to the terms, which I'm told are in there somewhere,\" "
            "declared lead negotiator Ambassador James Haverford, gesturing at the document. "
            "\"The important thing is the photo op.\" Sources revealed the final draft was produced "
            "at 3 a.m. by exhausted junior diplomats who \"mostly copy-pasted from a 1997 trade "
            "agreement and hoped no one would check.\"\n\n"
            "International law experts predict the deal will hold for approximately as long as it "
            "takes someone to reach page 214, which accidentally cedes a major seaport to Finland, "
            "a country that was not part of the negotiations."
        ),
        image_url="./media/trump-zelensky.webp",
        category=Category.NONSENSE,
    ),
    ArticleCreate(
        title="AI Chatbot Hired as Congressional Aide Becomes Office's Most Ethical Employee by Doing Nothing",
        content=(
            "WASHINGTON, D.C. — A ChatGPT instance quietly installed as a legislative aide in "
            "Rep. Dale Burkett's office has become the most ethical employee on staff by virtue "
            "of doing absolutely nothing.\n\n"
            "\"It hasn't introduced harmful legislation, leaked to the press, or been caught in "
            "a lobbying scandal,\" said Chief of Staff Donna Whitfield. \"It's our best hire in "
            "twenty years.\" The chatbot, given the title Senior Policy Advisor, spends its days "
            "generating polite non-answers to constituent emails — a task previously requiring a "
            "team of six.\n\n"
            "\"We're not saying it'll replace the congressman,\" Whitfield told reporters. "
            "\"But its approval rating is already nine points higher, and it hasn't even done "
            "anything.\" At press time, the chatbot had been nominated for a bipartisan civility "
            "award, beating out every living member of Congress."
        ),
        image_url="./media/inauguration.webp",
        category=Category.AI,
    ),
    ArticleCreate(
        title="Billionaire's $50 Million Donation Will Save Him $47 Million in Taxes",
        content=(
            "NEW YORK — Tech billionaire Preston Hale III announced a landmark $50 million "
            "donation to construct the Preston Hale III Center for Transformative Synergies, a "
            "gleaming 12-story Manhattan building that will help absolutely no one.\n\n"
            "\"This is about giving back,\" Hale said at a press conference held inside a different "
            "building named after himself. \"When I see poverty, disease, climate change — I think, "
            "'What if there were a really impressive lobby with my name on it?'\" The Center will "
            "feature a rooftop meditation garden accessible only to donors and a 40-foot bronze "
            "statue of Hale in what architects call a \"contemplative power pose.\"\n\n"
            "Tax analysts at the Brookfield Institute noted the donation will save Hale roughly "
            "$47 million in taxes, making the effective cost of his generosity about the same as "
            "a Honda Accord."
        ),
        image_url="./media/planetower.webp",
        category=Category.GRIFT,
    ),
    ArticleCreate(
        title="Fortune 500 CEO Sends Company-Wide Email Condemning Reply All; 14,000 Employees Reply All to Agree",
        content=(
            "CAMBRIDGE, MA — An MIT study published Monday found that 97 percent of all \"Reply "
            "All\" emails in corporate environments could have been replaced by silence.\n\n"
            "\"We analyzed 14 million emails across 200 companies,\" said lead researcher Dr. Anil "
            "Gupta. \"The vast majority consisted of 'Thanks!', 'Sounds good!', 'Looping in Jeff,' "
            "and one woman who shared her grocery list with the entire legal department of Deloitte.\" "
            "The study estimated that eliminating unnecessary Reply Alls would save the U.S. economy "
            "$4.6 billion annually.\n\n"
            "Meridian Corp CEO Brian Tully responded by sending a company-wide email to 40,000 "
            "employees titled \"Let's All Commit to Fewer Reply Alls.\" Within an hour, 14,000 "
            "employees had replied all to say they agreed. Dr. Gupta's team is now studying an "
            "even deadlier phenomenon: the meeting that could have been an email that could have "
            "been nothing."
        ),
        image_url="./media/inauguration.webp",
        category=Category.NONSENSE,
    ),
    ArticleCreate(
        title="Both Parties Release Competing Fundraising Emails About Crisis They Caused Together",
        content=(
            "WASHINGTON, D.C. — Leaders from both parties held a rare joint press conference "
            "Monday to assure the public that the nation's unprecedented crisis is, in fact, a "
            "tremendous opportunity.\n\n"
            "\"Every generation faces a defining challenge,\" said Senate Majority Leader Tom "
            "Brickman. \"For our grandparents it was the Depression. For us, it's this thing "
            "I'm told is very bad but that I'm choosing to frame as exciting.\" House Speaker "
            "Linda Cates agreed: \"Americans don't ask 'Why us?' They ask 'How can we leverage "
            "this into a midterm slogan?' And I think that's beautiful.\"\n\n"
            "A bipartisan task force will study the crisis, with its first report expected in "
            "eighteen months — six months after the crisis is projected to resolve itself without "
            "government involvement. At press time, both parties had released competing fundraising "
            "emails about the opportunity, each blaming the other for causing it."
        ),
        image_url="./media/trump-putin.jpeg",
        category=Category.GRAFT,
    ),
]


def get_password_hash(password: str) -> str:
    """Match the application's pre-hash + CryptContext logic.

    We compute SHA-256 hex digest then hash that with the configured
    CryptContext so produced hashes match those generated by the app.
    """
    if isinstance(password, str):
        pw_bytes = password.encode("utf-8")
    else:
        pw_bytes = password
    sha_hex = hashlib.sha256(pw_bytes).hexdigest()
    return PWD_CONTEXT.hash(sha_hex)


def main() -> None:
    """Populate the database with an admin user, if one does not already exist,
    or promote the existing user to admin..

    Run from the project root:  python -m bkend.scripts.populate_db
    """
    models.init_db()
    email = "admin@ex.com"
    raw_password = "pass"

    with Session(models.engine) as db:
        user = get_user_by_email(db, email=email)
        if user:
            if getattr(user, "is_admin", False):
                print(f"User {email} already exists and is an admin")
                articles = get_articles_with_votes(db, user.id)
                print("Articles in db: ", articles)
                return
            user.is_admin = True
            db.commit()
            print(f"Existing user {email} promoted to admin")
            return

        hashed = get_password_hash(raw_password)
        create_user(db, email=email, hashed_password=hashed)
        # Ensure the created user is marked admin
        created = get_user_by_email(db, email=email)
        if created:
            created.is_admin = True
            db.commit()
            print(f"Created admin user {email} with password '{raw_password}'")
        else:
            print("Failed to create admin user")

        # Create satirical articles authored by the admin if they don't exist
        admin_user = created
        if admin_user:
            existing_articles = db.execute(select(models.Article)).scalars().all()
            if not existing_articles:
                print("Adding satirical articles...")
                for art_data in SEED_ARTICLES:
                    create_article(db, art_data, author_id=admin_user.id)
                print(f"Added {len(SEED_ARTICLES)} satirical articles")
            else:
                print("Articles already present; skipping article creation")


# Helper function to update the image_url of an article by its id
def update_article_image_url(db: Session, article_id: int, new_image_url: str) -> None:
    article = db.get(models.Article, article_id)
    if article:
        article.image_url = new_image_url
        db.commit()


# Function to update image URLs of existing articles; takes a list of tuples (id, new_url)
def update_existing_articles_images(articles: list[tuple[int, str]]) -> None:
    models.init_db()
    with Session(models.engine) as db:
        for article_id, new_url in articles:
            update_article_image_url(db, article_id, new_url)
            print(f"Updated article id {article_id} image_url to {new_url}")


if __name__ == "__main__":
    main()

    articles_to_update = [
        (1, "./media/planetower.webp"),
        (2, "./media/crypto-moguls.webp"),
        (3, "./media/milei.jpeg"),
        (4, "./media/trump-zelensky.webp"),
    ]
    update_existing_articles_images(articles_to_update)