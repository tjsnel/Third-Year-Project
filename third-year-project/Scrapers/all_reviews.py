from review_scrape import ReviewScrape, GuardianReviewScrape, GenreReviewScrape, PitchforkReviewScrape, \
    NMEReviewScrape
import pandas as pd

# pitchfork_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\urls_shared.csv",
#                            index_col=0)
# pitchfork_scrape = PitchforkReviewScrape(df=pitchfork_df,
#                                          platform="Pitchfork",
#                                          header_tag="div",
#                                          header_class={"class": "BaseWrap-sc-UrHlS BaseText-fFrHpW "
#                                                                 "SplitScreenContentHeaderDekDown-fkATUS "
#                                                                 "boMZdO kqRnRO fZZtlk"},
#                                          body_tag="div",
#                                          body_class="body__inner-container",
#                                          score_tag="div",
#                                          score_class1={"class": "ScoreCircle-cIILhI hUIQbu"},
#                                          score_class2={"class": "ScoreCircle-cIILhI hHVylS"},
#                                          genre_tag="p",
#                                          genre_class={
#                                              "class": "BaseWrap-sc-UrHlS BaseText-fFrHpW InfoSliceValue-gTHtZf "
#                                                       "boMZdO cdnzYc jNiPXA"})
#
# pitchfork_scrape.get_data()
# pitchfork_scrape.write_records()

guardian_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\"
                          "urls_shared.csv",
                          index_col=0)
guardian_scrape = GuardianReviewScrape(df=guardian_df,
                                       platform="Guardian",
                                       header_tag="div",
                                       header_class={"class": "dcr-1aw10i3"},
                                       body_tag=["div", "span", "span", "p"],
                                       body_class=[{"class": "dcr-1f36xae"}, {"class": "dcr-wio59t"},
                                                   {"class": "dcr-1gj3hdi"}, {"class": "dcr-1gj3hdi"}],
                                       score_tag="path",
                                       score_class={"fill": "transparent"},
                                       genre_tag="li",
                                       genre_class={"class": "dcr-1ffx2ie"})

guardian_scrape.get_data()
guardian_scrape.write_records()

# spectrum_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\"
#                           "urls_shared.csv",
#                           index_col=0)
# spectrum_scrape = ReviewScrape(df=spectrum_df,
#                                platform="Spectrum",
#                                body_tag="div",
#                                body_class={"class": "bdaia-post-content"},
#                                score_tag="span",
#                                score_class={"class": "num rating-value"})
#
# spectrum_scrape.get_data()
# spectrum_scrape.write_records()
#
# nme_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\urls_shared.csv",
#                      index_col=0)
# nme_scrape = NMEReviewScrape(df=nme_df,
#                              platform="NME",
#                              header_tag="div",
#                              header_class={"class": "tdb-block-inner td-fix-index"},
#                              body_tag="div",
#                              body_class={"class": "tdb-block-inner td-fix-index"},
#                              score_tag="i",
#                              score_class={"class": "td-icon-star"})
#
# nme_scrape.get_data()
# nme_scrape.write_records()
