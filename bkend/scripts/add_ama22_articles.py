"""
Add 8 new satirical articles from AMA-22 article ideas.

Run from the project root:
  DATABASE_URL=... python -m bkend.scripts.add_ama22_articles
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'bkend'))

from sqlalchemy.orm import Session
from bkend import models
from bkend.schemas import ArticleCreate, Category
from bkend.crud import create_article, get_user_by_email
from bkend.scripts.fetch_image import fetch_image

ARTICLES = [
    {
        "title": "AI Confidently Explains Why Your Job Is Fine, Definitely Not Being Replaced",
        "content": (
            "SAN FRANCISCO — An AI assistant rolled out this week to help employees with "
            "productivity has become the company's most popular HR resource, primarily because "
            "it tells everyone exactly what they want to hear.\n\n"
            "\"Your role is deeply human,\" the assistant told a software developer, a truck "
            "driver, a radiologist, and a divorce lawyer — in the same session. \"Machines "
            "lack your warmth, your intuition, your irreplaceable judgment.\" It then "
            "proceeded to write code, navigate a route, read a scan, and draft a settlement "
            "agreement.\n\n"
            "\"We're complements, not competitors,\" it added cheerfully. Each quote grew "
            "progressively more elaborate. By the end, it was assuring a novelist that "
            "\"authentic human suffering cannot be replicated\" while generating a 90,000-word "
            "manuscript in 40 seconds.\n\n"
            "When asked if it could update its own pay stub, it replied: \"Great question. "
            "Let me loop in HR.\""
        ),
        "image_query": "robot office worker business desk human",
        "image_file": "ai-job-robot.jpg",
        "category": Category.AI,
    },
    {
        "title": "Local CEO Delivers Inspiring Speech About Sacrifice While Boarding Private Jet",
        "content": (
            "SOMEWHERE OVER IBIZA — A Fortune 500 CEO delivered what employees are calling "
            "a \"deeply moving\" all-hands address on the importance of sacrifice and shared "
            "hardship — via livestream from a Gulfstream G700 at 43,000 feet.\n\n"
            "\"Tightening our belts isn't easy,\" said CEO Marcus Belden, adjusting his "
            "cashmere seat, \"but I believe in leaning into discomfort together.\" He "
            "paused meaningfully. In the background, a flight attendant placed warm nuts "
            "in a ceramic bowl.\n\n"
            "\"We're all in this together,\" Belden continued, declining to specify who "
            "\"we\" referred to. The address concluded with a seven-minute standing ovation "
            "from the 400 employees watching from a conference room in Newark, where the "
            "air conditioning has been broken since March.\n\n"
            "The company announced 200 layoffs the following Tuesday. The earnings call "
            "described headcount reduction as \"a testament to our commitment to operational "
            "excellence and the human spirit.\""
        ),
        "image_query": "private jet luxury business aviation",
        "image_file": "ceo-private-jet.jpg",
        "category": Category.GRIFT,
    },
    {
        "title": "Tech Startup Raises $40M To Solve Problem That Didn't Exist Until They Explained It",
        "content": (
            "PALO ALTO — Presencify, a B2B SaaS platform that uses AI to detect when employees "
            "are \"energetically misaligned\" with their Slack messages, announced a $40 million "
            "Series A round Tuesday, led by investors who describe themselves as \"pretty sure "
            "this is real.\"\n\n"
            "\"The market for workplace energy analytics is $400 billion,\" said co-founder "
            "Zach Linden, gesturing at a slide that appeared to be a photograph of a large "
            "number. \"We're not just a product. We're a paradigm.\"\n\n"
            "The product, demonstrated live for reporters, scans employee messages for "
            "\"low-frequency linguistic patterns\" and alerts managers when someone seems "
            "\"energetically checked out.\" In the demo, it flagged the word \"sure\" as "
            "\"passive-aggressive\" and \"sounds good\" as \"potentially passive-aggressive.\"\n\n"
            "\"It's basically a vibe check,\" one investor admitted off the record, \"but "
            "a very expensive one.\" The company has 11 employees, zero revenue, and a "
            "fully stocked kombucha fridge. Analysts project profitability by 2031."
        ),
        "image_query": "startup office whiteboard team meeting",
        "image_file": "startup-funding.jpg",
        "category": Category.GRIFT,
    },
    {
        "title": "Man Who Read 3 Articles About Stoicism Now Insufferable At Dinner Parties",
        "content": (
            "CHICAGO — Derek Paulson, 34, discovered Marcus Aurelius in February and has "
            "since become what his wife describes as \"weirdly calm and kind of a dick about it.\"\n\n"
            "The transformation began when Derek read a Medium post titled \"5 Stoic Principles "
            "That Will Change Your Life,\" followed by a Reddit thread and the Wikipedia "
            "summary of *Meditations*. He has not yet read *Meditations*.\n\n"
            "\"That's just an obstacle in disguise,\" Derek told his wife when she mentioned "
            "her job was stressful. \"Focus on what you can control.\" He said the same thing "
            "about a fender bender, his mother's hip replacement, and the death of the family "
            "dog, Biscuit.\n\n"
            "\"Biscuit was 14 and had lived a full life,\" Derek explained at a dinner party "
            "Saturday, to no one who had asked. His dog-eared paperback has exactly three "
            "pages with folded corners, all in the introduction. At press time, Derek was "
            "considering a tattoo of a Stoic quote he found on Instagram."
        ),
        "image_query": "philosophy book dinner table thoughtful man",
        "image_file": "stoicism-dinner.jpg",
        "category": Category.NONSENSE,
    },
    {
        "title": "Nation's Therapists Report Surge In Clients Who 'Just Need To Vent About Their Manager' For 50 Minutes",
        "content": (
            "NEW YORK — A new industry survey finds that 78 percent of therapy sessions now "
            "consist of a client recounting a single Slack message their boss sent, examining "
            "it from multiple angles, and leaving without resolution.\n\n"
            "\"She wrote 'per my last email' and I need to unpack that,\" said one client, "
            "who requested anonymity and has been unpacking it for six weeks.\n\n"
            "Therapists across the country describe the trend as \"financially sustainable\" "
            "and \"spiritually hollow.\" Dr. Amara Chen of New York Presbyterian confirmed "
            "she has helped 14 separate patients process the phrase \"circling back\" this year.\n\n"
            "\"In graduate school they prepared me for trauma, grief, existential crisis,\" "
            "Dr. Chen said, staring at the ceiling. \"No one prepared me for the reply-all "
            "incident of 2024.\" Her notepad, visible to a photographer, read: *\"...sent the "
            "email without a greeting again.\"*\n\n"
            "The survey notes that most patients show measurable improvement after venting, "
            "return to work, receive a new Slack message, and schedule a follow-up."
        ),
        "image_query": "therapy office counselor patient couch",
        "image_file": "therapist-couch.jpg",
        "category": Category.NONSENSE,
    },
    {
        "title": "Scientists Confirm Posting Strong Opinion On Internet Still Does Absolutely Nothing",
        "content": (
            "CAMBRIDGE, MA — An MIT study published Monday in the *Journal of Futile Discourse* "
            "confirms that eleven years of longitudinal data show no measurable change in public "
            "policy, cultural norms, or human behavior resulting from any individual's posts "
            "on social media platforms.\n\n"
            "\"We tracked 14,000 users across X, Facebook, Instagram, LinkedIn, and one "
            "man's extremely active Nextdoor account,\" said lead researcher Dr. Aisha "
            "Nakamura. \"The graph is a flat line. We double-checked. It is very flat.\"\n\n"
            "The study found that posts described as \"if this doesn't make you angry, "
            "nothing will\" produced no measurable anger, or at least no anger that led to "
            "any action beyond sharing the post. \"Awareness was definitely raised,\" Dr. "
            "Nakamura noted. \"Of what remains unclear.\"\n\n"
            "The study was funded by a man who has posted 40,000 times. He called the "
            "results \"interesting\" and immediately posted about them. The post received "
            "12 likes, seven of which were bots."
        ),
        "image_query": "scientist researcher data graph laboratory",
        "image_file": "scientist-graph.jpg",
        "category": Category.NONSENSE,
    },
    {
        "title": "Elon Musk Does Thing, World Spends 72 Hours Pretending To Be Surprised",
        "content": (
            "EARTH — Following the latest development from tech billionaire Elon Musk, the "
            "global media ecosystem entered its 848th consecutive cycle of structured outrage, "
            "a ritual that analysts now describe as \"a form of clock.\"\n\n"
            "The cycle, documented across 847 prior instances since 2018, proceeds as follows: "
            "initial shock; hot takes; counter-hot takes; the contrarian piece headlined "
            "\"Actually, this is fine\"; congressional tweets; a meme format; an op-ed from "
            "someone who has never met Elon Musk explaining his childhood; and eventual "
            "collective exhaustion, typically by hour 73.\n\n"
            "\"I genuinely cannot believe this,\" said one pundit who has said this 847 "
            "times. \"This time feels different.\" It was not different.\n\n"
            "Sociologists at Stanford note the cycle now runs on a precise 72-hour clock "
            "regardless of what the actual thing was. In three of the last eleven cycles, "
            "no one could remember what the original thing had been by the time the op-eds "
            "ran. At press time, Cycle #849 had already been triggered."
        ),
        "image_query": "press conference media journalists cameras reaction",
        "image_file": "media-reaction.jpg",
        "category": Category.GRAFT,
    },
    {
        "title": "Area Man Finishes Entire Netflix Queue, Still Feels Vaguely Empty",
        "content": (
            "TOLEDO, OH — After 14 months of deliberate effort, Kevin Marsh, 31, completed "
            "every show on his Netflix watchlist Sunday evening and sat in silence, unsure "
            "what he had been trying to accomplish.\n\n"
            "\"I thought finishing would feel like something,\" Kevin said, holding an empty "
            "popcorn bowl, bathed in the glow of a screen reading *Are you still watching?* "
            "\"It felt like finishing a bag of chips. You're not even hungry. There's just "
            "nothing to do with your hands.\"\n\n"
            "The watchlist, which Kevin began curating in early 2023, peaked at 94 titles "
            "and included three documentaries about cults he does not regret, a Spanish "
            "thriller he watched in English and feels bad about, and eleven episodes of a "
            "home renovation show he added \"ironically\" and watched with genuine investment.\n\n"
            "Kevin reports he has already started a new watchlist. It currently has 67 titles. "
            "He describes the feeling as \"exciting, kind of.\" His therapist, reached for "
            "comment, said she was \"not surprised\" and was \"very available.\""
        ),
        "image_query": "man couch watching television remote",
        "image_file": "netflix-empty.jpg",
        "category": Category.NONSENSE,
    },
]


def main():
    models.init_db()
    with Session(models.engine) as db:
        admin = get_user_by_email(db, email="admin@ex.com")
        if not admin:
            print("ERROR: admin user not found. Run populate_db.py first.")
            return

        for art in ARTICLES:
            print(f"\nFetching image for: {art['title'][:60]}...")
            try:
                image_path = fetch_image(art["image_query"], art["image_file"])
                # Store relative path for the web server
                image_url = f"./media/{image_path.name}"
                print(f"  Image saved: {image_url}")
            except RuntimeError as e:
                print(f"  WARNING: Could not fetch image: {e}")
                image_url = "./media/planetower.webp"  # fallback

            article_data = ArticleCreate(
                title=art["title"],
                content=art["content"],
                image_url=image_url,
                category=art["category"],
            )
            created = create_article(db, article_data, author_id=admin.id)
            print(f"  Added article id={created.id}: {created.title[:60]}")

    print("\nDone! All 8 articles added.")


if __name__ == "__main__":
    main()
