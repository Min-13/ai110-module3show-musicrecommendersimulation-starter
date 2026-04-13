# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

RhythmRank 1.0

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

This recommender gives song suggestions based on what kind of music a user says they want, like genre, mood, energy, acoustic feel, or instrumental style. It assumes the user already knows their preferences and that the song features in the dataset are a good enough way to describe taste. The system is mainly for classroom practice, not for real users on a music platform. It is meant to help explore how recommendation systems work and where they can go wrong.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The recommender looks at features of each song like genre, mood, energy level, acoustic feel, instrumentalness, popularity, and release year. It also looks at what the user asks for, such as favorite genre, preferred mood, target energy, whether they like acoustic songs, want instrumental tracks, prefer newer music, or want popular songs only. Each song gets points when it matches those preferences closely, and songs that match more areas get higher scores. Compared to the starter version, I added more features, gave stronger weight to some matches like genre, included filters like popularity and year, and made the scoring more detailed instead of only checking a few simple traits.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The dataset has 20 songs in the catalog. It includes different genres like pop, lofi, rock, hip-hop, jazz, country, folk, metal, classical, reggae, blues, and electronic, along with moods like happy, chill, focused, peaceful, nostalgic, intense, dreamy, and romantic. I expanded the starter data by adding more songs, more genres, more moods, and extra features like popularity, year, instrumentalness, and speechiness. Even with those additions, the dataset is still small, so many parts of musical taste are missing, such as global music styles, underground artists, personal favorites, and more diverse moods or listening situations.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works best for users with clear preferences like wanting happy pop songs, calm lofi study music, or high-energy workout tracks. It does a good job matching obvious patterns such as low-energy plus instrumental leading to chill focus songs, or high-energy plus pop leading to upbeat songs. The scoring also captures mood and genre combinations fairly well when the user profile is simple and consistent. In several tests, the recommendations matched intuition, like Focus Flow showing up for study vibes or Gym Hero appearing for energetic workout profiles.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The system struggles because it does not consider things like lyrics, artist similarity, listening history, tempo preference, or whether someone wants variety. Some genres and moods are underrepresented since the dataset is small, so users who like niche styles may get weak recommendations. It can also overfit to one preference, especially genre, where an exact genre match can rank higher than a song that better matches mood or energy. The scoring may also favor users who like popular, newer, or common genres more than users with mixed or unusual tastes.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

Profile 1 vs Profile 2: Profile 1 returns upbeat pop songs like Sunrise City and Rooftop Lights because the user asked for high energy and happy mood. Profile 2 shifts toward softer acoustic and instrumental songs like Porch Song and Focus Flow because those settings reward calm, organic, low-vocal tracks.

Profile 2 vs Profile 3: Profile 2 has many calm choices because the popularity filter is low, so the system can search the full catalog. Profile 3 only returns two songs because the popularity floor is very high, which removes most of the dataset before scoring even begins.

Profile 3 vs Profile 4: Profile 3 mostly recommends mainstream high-popularity songs because popularity becomes the strongest filter. Profile 4 uses an unknown mood, so the system falls back to other features like genre, acousticness, and energy, which is why songs like Coffee Shop Stories rise to the top.

Profile 4 vs Profile 5: Profile 4 prefers medium-energy acoustic songs, so it returns folk, jazz, and blues style tracks. Profile 5 asks for extremely low energy, so the ranking shifts toward the calmest songs in the catalog like Spacewalk Thoughts and Moonlight Revisited.

Profile 5 vs Profile 6: Profile 5 rewards peaceful and low-energy music, so mellow songs dominate. Profile 6 has genre and mood pointing in opposite directions, so the system mixes aggressive genre matches like Iron Horizon with calmer mood matches like Island Morning, showing how conflicting preferences split the results.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

I would improve the model by adding more features like tempo, lyrics style, favorite artists, listening history, and whether the user wants familiar songs or new discoveries. I would also make explanations better by showing the top reasons a song matched and what preferences mattered most. Another goal would be improving diversity so the top results are not all from the same genre or artist. I would also make it better at handling mixed tastes, such as users who like both calm study music and energetic workout songs depending on the situation.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

My biggest learning moment was realizing that recommendation systems are mostly built from choices about data, scoring rules, and weights. Even small changes in those settings could completely change which songs ranked first. AI tools helped me brainstorm ideas, debug code, and improve explanations faster, but I still had to double-check the logic, test outputs, and make sure the code actually matched my goals. I was surprised that even a simple scoring system could feel like a real recommender when the results matched the user’s mood or activity. If I extended this project, I would add a larger dataset, more user preferences, better diversity in results, and feedback learning based on what users actually like or skip.