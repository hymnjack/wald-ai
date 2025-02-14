import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.markdown import Markdown

from src.core.schemas import ResearchConfig
from src.core.research_engine import ResearchEngine
from src.core.feedback import generate_feedback
from src.integrations.firecrawl_client import FirecrawlClient

# Initialize rich console for pretty output
console = Console()

def update_progress(progress_bar, task_id):
    def callback(progress):
        total = progress.total_depth * progress.total_breadth
        current = (progress.current_depth - 1) * progress.total_breadth + progress.current_breadth
        progress_bar.update(
            task_id,
            completed=current,
            total=total,
            description=f"Depth {progress.current_depth}/{progress.total_depth}"
        )
    return callback

async def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.getenv("FIRECRAWL_KEY"):
        console.print("[red]Error: FIRECRAWL_KEY not found in environment variables[/red]")
        return
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not found in environment variables[/red]")
        return

    # Get user input
    console.print("[bold blue]Deep Research CLI[/bold blue]")
    query = console.input("[yellow]Enter your research query: [/yellow]")
    
    # Fixed values for depth and breadth
    breadth = 3  # Fixed at 3
    depth = 2    # Fixed at 2

    # Generate follow-up questions
    console.print("\n[bold]Generating follow-up questions...[/bold]")
    questions = await generate_feedback(query)
    
    # Collect answers
    console.print("\n[bold]To better understand your research needs, please answer these follow-up questions:[/bold]")
    answers = []
    for question in questions:
        answer = console.input(f"\n[yellow]{question}[/yellow]\nYour answer: ")
        answers.append(answer)
    
    # Combine all information
    combined_query = (
        f"Initial Query: {query}\n"
        "Follow-up Questions and Answers:\n" +
        "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(questions, answers))
    )

    # Initialize components
    client = FirecrawlClient(api_key=os.getenv("FIRECRAWL_KEY"))
    
    # Create progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        # Add main progress task
        task_id = progress.add_task("Starting research...", total=100)
        
        # Initialize research engine with progress callback
        engine = ResearchEngine(
            firecrawl_client=client,
            on_progress=update_progress(progress, task_id)
        )
        
        # Run research
        try:
            config = ResearchConfig(
                query=combined_query,
                breadth=breadth,
                depth=depth
            )
            result = await engine.research(config)
            
            # Display results
            console.print("\n[bold green]Research Complete![/bold green]")
            
            # Save and display the report
            console.print("\n[bold]Research Report:[/bold]")
            console.print(Markdown(result.final_report))
            
            # Save to file
            with open("output.md", "w") as f:
                f.write(result.final_report)
            console.print("\n[bold green]Report saved to output.md[/bold green]")
            
            console.print("\n[bold]Key Learnings:[/bold]")
            for i, learning in enumerate(result.learnings, 1):
                console.print(f"{i}. {learning}")
            
            console.print("\n[bold]Sources:[/bold]")
            for url in result.visited_urls:
                console.print(f"- {url}")
                
        except Exception as e:
            console.print(f"\n[red]Error during research: {str(e)}[/red]")
        finally:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())