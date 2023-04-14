from full_scrape import FullScrape, GuardianFullScrape, GenreFullScrape, PitchforkFullScrape, \
    NMEFullScrape
import pandas as pd

pitchfork_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                           "Data\\Pitchforkurls.csv",
                           index_col=0)
pitchfork_scrape = PitchforkFullScrape(df=pitchfork_df,
                                       platform="Pitchfork",
                                       base_url="https://pitchfork.com/",
                                       score_tag="div",
                                       score_class1={"class": "ScoreCircle-cIILhI hUIQbu"},
                                       score_class2={"class": "ScoreCircle-cIILhI hHVylS"},
                                       genre_tag="p",
                                       genre_class={
                                           "class": "BaseWrap-sc-UrHlS BaseText-fFrHpW InfoSliceValue-gTHtZf "
                                                    "boMZdO cdnzYc jNiPXA"})

pitchfork_scrape.get_data()
pitchfork_scrape.write_records()

guardian_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\"
                          "Guardianurls.csv",
                          index_col=0)
guardian_scrape = GuardianFullScrape(df=guardian_df,
                                     platform="Guardian",
                                     score_tag="path",
                                     score_class={"fill": "transparent"},
                                     genre_tag="a",
                                     genre_class={"class": "dcr-viu5to"},
                                     base_url="")

guardian_scrape.get_data()
guardian_scrape.write_records()

spectrum_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                           "Data\\Spectrumurls.csv",
                          index_col=0)
spectrum_scrape = FullScrape(df=spectrum_df,
                             platform="Spectrum",
                             score_tag="span",
                             score_class={"class": "num rating-value"},
                             base_url="")

spectrum_scrape.get_data()
spectrum_scrape.write_records()

nme_df = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                           "Data\\NMEurls.csv",
                     index_col=0)
nme_scrape = NMEFullScrape(df=nme_df,
                           platform="NME",
                           score_tag="i",
                           score_class={"class": "td-icon-star"},
                           base_url="")

nme_scrape.get_data()
nme_scrape.write_records()
