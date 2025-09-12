from enum import Enum

class SlideLayout(str, Enum):
    """Predefined slide layouts for PowerPoint presentations."""

    # Basic Layouts
    TITLE_ONLY = "titleonly"  # Clean slide with only a centered title, ideal for section breaks and dramatic emphasis
    BULLET_LIST = "bulletlist"  # Traditional layout with title and bulleted content, perfect for listing key points or agenda items
    TITLE_AND_CONTENT = "titleandcontent"  # Versatile layout with title and flexible content area for text, images, or mixed media
    
    # Multi-Column Layouts
    TWO_COLUMN = "twocolumn"  # Split content layout for side-by-side comparisons, before/after scenarios, or balanced information
    THREE_COLUMN = "threecolumn"  # Triple column layout for organizing information into three distinct categories or sections
    
    # Visual-Heavy Layouts
    IMAGE_AND_TEXT = "imageandtext"  # Balanced layout combining visual elements with descriptive text for storytelling
    FULL_IMAGE = "fullimage"  # Image-dominant layout with minimal text overlay, ideal for visual impact and emotional connection
    IMAGE_GRID = "imagegrid"  # Grid of multiple images with captions, perfect for showcasing products, portfolios, or examples
    
    # Specialized Content Layouts
    COMPARISON = "comparison"  # Side-by-side comparison layout with clear visual separation for contrasting options or alternatives
    QUOTE = "quote"  # Emphasis layout for testimonials, quotes, or key statements with prominent typography and attribution
    STATISTICS = "statistics"  # Data-focused layout optimized for displaying numbers, percentages, and key metrics prominently
    TIMELINE = "timeline"  # Chronological layout for process flows, project milestones, or historical progression
    
    # Process and Flow Layouts
    STEP_BY_STEP = "stepbystep"  # Sequential process layout with numbered steps and clear progression indicators
    FLOWCHART = "flowchart"  # Diagram-based layout for decision trees, workflows, and process visualization
    PYRAMID = "pyramid"  # Hierarchical layout showing progression from broad concepts to specific details or vice versa
    
    # Presentation Structure Layouts
    AGENDA = "agenda"  # Structured layout for presentation outlines with clear sections and timing information
    CONCLUSION = "conclusion"  # Summary layout for key takeaways, action items, and final thoughts with strong visual hierarchy
    THANK_YOU = "thankyou"  # Closing slide layout with contact information and acknowledgments
    
    # Interactive and Engagement Layouts
    QUESTION = "question"  # Layout designed to pose questions to audience with clear, readable text and engagement prompts
    POLL = "poll"  # Interactive layout for audience participation with voting options and results display
    CONTACT = "contact"  # Information-rich layout for sharing contact details, social media, and next steps
    
    # Data Visualization Layouts
    CHART = "chart"  # Chart-focused layout with title, chart area, and space for data insights or conclusions
    GRAPH_AND_TEXT = "graphandtext"  # Balanced layout combining data visualizations with explanatory text and analysis
    DASHBOARD = "dashboard"  # Multi-metric layout displaying key performance indicators and data summaries in a grid format
    TABLE = "table"  # Structured data layout with clear headers and organized rows for detailed information presentation
    
    # Creative and Design Layouts
    ICON_GRID = "icongrid"  # Visual layout using icons with labels to represent concepts, services, or features clearly
    HERO_IMAGE = "heroimage"  # Large background image with overlay text for emotional impact and brand storytelling
    SPLIT_SCREEN = "splitscreen"  # Dramatic divided layout contrasting two concepts, products, or time periods
    MAGAZINE_STYLE = "magazinestyle"  # Editorial layout with mixed text sizes, images, and white space for visual interest
    
    # Educational and Training Layouts
    LESSON = "lesson"  # Educational layout with learning objectives, content sections, and knowledge check areas
    TUTORIAL = "tutorial"  # Step-by-step instructional layout with screenshots, arrows, and detailed explanations
    CASE_STUDY = "casestudy"  # Problem-solution format with background, challenge, approach, and results sections
    EXERCISE = "exercise"  # Interactive learning layout with instructions, workspace, and solution areas
    
    # Business and Corporate Layouts
    PITCH = "pitch"  # Investor-focused layout emphasizing problem, solution, market size, and business model
    TEAM = "team"  # Personnel showcase layout with photos, names, roles, and brief professional backgrounds
    PORTFOLIO = "portfolio"  # Project showcase layout highlighting work samples, achievements, and client testimonials
    ROADMAP = "roadmap"  # Strategic planning layout showing milestones, dependencies, and timeline visualization
    
    # Marketing and Sales Layouts
    PRODUCT_SHOWCASE = "productshowcase"  # Product-centric layout with high-quality images, features, and benefits
    TESTIMONIAL = "testimonial"  # Customer feedback layout with quotes, attribution, and credibility indicators
    PRICING = "pricing"  # Comparative pricing layout with tiers, features, and clear call-to-action elements
    BEFORE_AFTER = "beforeafter"  # Transformation layout showing clear contrast and improvement results
    
    # Technical and Scientific Layouts
    TECHNICAL_DIAGRAM = "technicaldiagram"  # Complex system visualization with labels, connections, and detailed annotations
    RESEARCH_FINDINGS = "researchfindings"  # Academic layout presenting methodology, data, analysis, and conclusions
    ARCHITECTURE = "architecture"  # System or building design layout with blueprints, specifications, and components
    FORMULA = "formula"  # Mathematical or scientific equation layout with derivations and practical applications
    
    # Event and Schedule Layouts
    SCHEDULE = "schedule"  # Time-based layout showing agenda items, speakers, locations, and duration details
    EVENT_OVERVIEW = "eventoverview"  # Comprehensive event layout with highlights, logistics, and participant information
    CALENDAR = "calendar"  # Date-based layout showing important deadlines, milestones, and recurring activities
    
    # Storytelling and Narrative Layouts
    STORY_ARC = "storyarc"  # Narrative structure layout following beginning, middle, end with character or plot development
    PROBLEM_SOLUTION = "problemsolution"  # Challenge-resolution layout emphasizing pain points and proposed fixes
    JOURNEY_MAP = "journeymap"  # User or customer experience layout showing touchpoints, emotions, and opportunities