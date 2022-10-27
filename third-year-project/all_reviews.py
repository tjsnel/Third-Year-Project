from review_scrape import ReviewScrape, GuardianReviewScrape, GenreReviewScrape
import pandas as pd

pitchfork_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\Pitchforkurls.csv")
pitchfork_scrape = GenreReviewScrape(df=pitchfork_df,
                                     platform="Pitchfork",
                                     header_tag="div",
                                     header_class={"class": "BaseWrap-sc-UrHlS BaseText-fFrHpW "
                                                            "SplitScreenContentHeaderDekDown-fkATUS "
                                                            "boMZdO kqRnRO fZZtlk"},
                                     body_tag="div",
                                     body_class="body__inner-container",
                                     score_tag="p",
                                     score_class={
                                         "class": "BaseWrap-sc-UrHlS BaseText-fFrHpW Rating-cIWDua boMZdO ehZJoO "
                                                  "ixrqwp"},
                                     genre_tag="p",
                                     genre_class={"class": "BaseWrap-sc-UrHlS BaseText-fFrHpW InfoSliceValue-gTHtZf "
                                                           "boMZdO cdnzYc jNiPXA"})

guardian_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\Guardianurls.csv")
guardian_scrape = GuardianReviewScrape(df=guardian_df,
                                       platform="Guardian",
                                       header_tag="div",
                                       header_class={"class": "dcr-1aw10i3"},
                                       body_tag="div",
                                       body_class={"class": "dcr-hw2voq"},
                                       score_tag="path",
                                       score_class={"fill": "transparent"},
                                       genre_tag="li",
                                       genre_class={"class": "dcr-1jcr6mo"})

guardian_scrape.get_data()
guardian_scrape.write_records()
