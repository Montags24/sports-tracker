from app import app, db
from app.models import User, Sport, InstagramPosts
from instascrape import Profile


def reset_users():
    with app.app_context():
        users = User.query.all()

        for user in users:
            user.sport_id = None
            user.sign_up_timestamp = None
            user.attended_sport = False
            user.nominal_submitted = False
        db.session.commit()

def scrape_instagram_posts():
    profile = Profile('https://www.instagram.com/8_trg_bn_reme/')
    profile.scrape()
    profile_posts = profile.get_recent_posts()
    embeds = [post.embed() for post in profile_posts]
    print(embeds)
    with app.app_context():
        for embed in embeds:
            if not InstagramPosts.query.filter_by(embed=embed).first():
                post_embed = InstagramPosts(embed=embed)
                db.session.add(post_embed)
        db.session.commit()
        

if __name__ == "__main__":
    ...