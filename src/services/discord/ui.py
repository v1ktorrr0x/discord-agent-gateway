"""
Discord UI components (Views, Buttons, etc.).
"""

import discord
from typing import Optional, Callable, Awaitable

class ChatView(discord.ui.View):
    """
    Standard chat view with control buttons.
    """
    
    def __init__(
        self, 
        timeout: Optional[float] = None,
        reset_callback: Optional[Callable[[discord.Interaction], Awaitable[None]]] = None
    ):
        """
        Initialize the view.
        
        Args:
            timeout: Timeout in seconds
            reset_callback: Async function to call when reset is clicked
        """
        super().__init__(timeout=timeout)
        self.reset_callback = reset_callback

    @discord.ui.button(
        label="Reset Context", 
        style=discord.ButtonStyle.secondary, 
        emoji="🧹",
        custom_id="reset_context_btn"
    )
    async def reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle reset button click."""
        if self.reset_callback:
            # Acknowledge immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)
            await self.reset_callback(interaction)
        else:
            await interaction.response.send_message("Reset function not configured.", ephemeral=True)

    @discord.ui.button(
        label="Help",
        style=discord.ButtonStyle.secondary,
        emoji="❓",
        custom_id="help_btn"
    )
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle help button click."""
        help_msg = (
            "**Chat Bot Help**\n"
            "- I remember our conversation history.\n"
            "- Click **Reset Context** to clear my memory of this chat.\n"
            "- I split long messages automatically."
        )
        await interaction.response.send_message(help_msg, ephemeral=True)
