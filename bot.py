import discord
from discord import app_commands, ui
from discord.ext import commands
import aiosqlite
import datetime

#admn ids = division command, HC, & LS. for case management (deleting case) 
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                detective TEXT,
                suspect TEXT,
                charges TEXT,
                narrative TEXT,
                status TEXT,
                timestamp TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS case_jackets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                url TEXT,
                label TEXT,
                added_by TEXT
            )
        """)
        await db.commit()

async def get_next_case_id(dept_code: str):
    now = datetime.datetime.now()
    year_prefix = now.strftime("%y")
    pattern = f"{year_prefix}-{dept_code}-%"
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT case_id FROM cases WHERE case_id LIKE ?", (pattern,))
        rows = await cursor.fetchall()
    if not rows:
        return f"{year_prefix}-{dept_code}-001"
    max_num = 0
    for row in rows:
        try:
            num = int(row[0].split('-')[2])
            if num > max_num: max_num = num
        except (IndexError, ValueError): continue
    return f"{year_prefix}-{dept_code}-{max_num + 1:03d}"

class CasePaginator(ui.View):
    def __init__(self, cases, chunk_size=5):
        super().__init__(timeout=60)
        self.cases = cases
        self.chunk_size = chunk_size
        self.current_page = 0
        self.max_pages = (len(cases) - 1) // chunk_size + 1

    def create_embed(self):
        start = self.current_page * self.chunk_size
        end = start + self.chunk_size
        chunk = self.cases[start:end]
        embed = discord.Embed(title="Case Directory", color=discord.Color.blue())
        embed.set_footer(text=f"Page {self.current_page + 1} of {self.max_pages}")
        for case in chunk:
            embed.add_field(name=f"ID: {case[0]}", value=f"Suspect: {case[2]}\nStatus: {case[5]}", inline=False)
        return embed

    @ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def previous_page(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("First page reached.", ephemeral=True)

    @ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next_page(self, interaction: discord.Interaction, button: ui.Button):
        if (self.current_page + 1) < self.max_pages:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("Last page reached.", ephemeral=True)

class CaseModal(ui.Modal, title='New Investigation'):
    def __init__(self, department: str):
        super().__init__()
        self.department = department
    suspect = ui.TextInput(label='Suspect Name', placeholder='Forename Surname')
    charges = ui.TextInput(label='Potential Charges', style=discord.TextStyle.paragraph)
    narrative = ui.TextInput(label='Incident Narrative', style=discord.TextStyle.paragraph, min_length=20)

    async def on_submit(self, interaction: discord.Interaction):
        case_id = await get_next_case_id(self.department)
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?)",
                (case_id, interaction.user.display_name, self.suspect.value, self.charges.value, self.narrative.value, "OPEN", datetime.datetime.now().isoformat()))
            await db.commit()
        embed = discord.Embed(title=f"📂 Case Opened: {case_id}", color=discord.Color.green())
        embed.add_field(name="Suspect", value=self.suspect.value)
        await interaction.response.send_message(embed=embed)

class EditModal(ui.Modal):
    def __init__(self, case_id, current_suspect, current_narrative):
        super().__init__(title=f"Editing Case: {case_id}")
        self.case_id = case_id
        self.suspect_input = ui.TextInput(label='Suspect Name', default=current_suspect)
        self.narrative_input = ui.TextInput(label='Narrative', style=discord.TextStyle.paragraph, default=current_narrative)
        self.add_item(self.suspect_input)
        self.add_item(self.narrative_input)

    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("UPDATE cases SET suspect = ?, narrative = ? WHERE case_id = ?",
                (self.suspect_input.value, self.narrative_input.value, self.case_id))
            await db.commit()
        await interaction.response.send_message(f"✅ Case {self.case_id} updated.", ephemeral=True)

class CIDBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
    async def setup_hook(self):
        await init_db()
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

client = CIDBot()

@client.tree.command(name="file_case", description="Open a new investigation file")
@app_commands.choices(department=[
    app_commands.Choice(name="CID - Criminal Investigation", value="CID"),
    app_commands.Choice(name="DTF - Drug Task Force", value="DTF")
])
async def file_case(interaction: discord.Interaction, department: app_commands.Choice[str]):
    if not any(role.id == CID_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("⛔ Unauthorized.", ephemeral=True)
    await interaction.response.send_modal(CaseModal(department=department.value))

@client.tree.command(name="edit_case", description="Update case status, suspect, or narrative")
@app_commands.choices(new_status=[
    app_commands.Choice(name="Keep Current Status", value="KEEP"),
    app_commands.Choice(name="OPEN", value="OPEN"),
    app_commands.Choice(name="CLOSED", value="CLOSED"),
    app_commands.Choice(name="COLD", value="COLD")
])
async def edit_case(interaction: discord.Interaction, case_id: str, new_status: app_commands.Choice[str]):
    if not any(role.id == CID_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("⛔ Unauthorized.", ephemeral=True)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT suspect, narrative FROM cases WHERE case_id = ?", (case_id,))
        row = await cursor.fetchone()
        if not row: return await interaction.response.send_message("❌ Not found.", ephemeral=True)
        if new_status.value != "KEEP":
            await db.execute("UPDATE cases SET status = ? WHERE case_id = ?", (new_status.value, case_id))
            await db.commit()
    await interaction.response.send_modal(EditModal(case_id, row[0], row[1]))

@client.tree.command(name="case_directory", description="View all current cases")
async def case_directory(interaction: discord.Interaction):
    if not any(role.id == CID_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("⛔ Unauthorized.", ephemeral=True)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT case_id, detective, suspect, charges, narrative, status FROM cases ORDER BY timestamp DESC")
        cases = await cursor.fetchall()
    if not cases: return await interaction.response.send_message("Database empty.", ephemeral=True)
    view = CasePaginator(cases)
    await interaction.response.send_message(embed=view.create_embed(), view=view)

@client.tree.command(name="case_lookup", description="View case dossier")
async def case_lookup(interaction: discord.Interaction, case_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        case = await cursor.fetchone()
        if not case: return await interaction.response.send_message("❌ Not found.", ephemeral=True)
        cursor = await db.execute("SELECT label, url FROM case_jackets WHERE case_id = ?", (case_id,))
        jackets = await cursor.fetchall()
    color = discord.Color.red() if "DTF" in case[0] else discord.Color.blue()
    embed = discord.Embed(title=f"📂 Case: {case[0]}", color=color)
    embed.add_field(name="Status", value=case[5], inline=True)
    embed.add_field(name="Suspect", value=case[2], inline=True)
    if jackets: embed.add_field(name="Jackets", value="\n".join([f"🔗 [{j[0]}]({j[1]})" for j in jackets]), inline=False)
    embed.add_field(name="Narrative", value=case[4][:1000], inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="add_jacket", description="Link document")
async def add_jacket(interaction: discord.Interaction, case_id: str, url: str, label: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO case_jackets (case_id, url, label, added_by) VALUES (?, ?, ?, ?)", (case_id, url, label, interaction.user.display_name))
        await db.commit()
    await interaction.response.send_message(f"✅ Linked {label}.", ephemeral=True)

@client.tree.command(name="add_evidence", description="Attach media link")
async def add_evidence(interaction: discord.Interaction, case_id: str, evidence_url: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT narrative FROM cases WHERE case_id = ?", (case_id,))
        row = await cursor.fetchone()
        if not row: return await interaction.response.send_message("❌ Not found.", ephemeral=True)
        new_nav = row[0] + f"\n\n**[EVIDENCE]** {interaction.user.display_name}: {evidence_url}"
        await db.execute("UPDATE cases SET narrative = ? WHERE case_id = ?", (new_nav, case_id))
        await db.commit()
    await interaction.response.send_message(f"✅ Evidence added.", ephemeral=True)

@client.tree.command(name="import_case", description="Import legacy records")
async def import_case(interaction: discord.Interaction, case_id: str, suspect: str, status: str):
    if not any(role.id == CID_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message("⛔ Unauthorized.", ephemeral=True)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?)",
            (case_id, interaction.user.display_name, suspect, "LEGACY", "Imported record.", status.upper(), datetime.datetime.now().isoformat()))
        await db.commit()
    await interaction.response.send_message(f"✅ Case {case_id} imported.", ephemeral=True)

@client.tree.command(name="delete_case", description="Delete record")
async def delete_case(interaction: discord.Interaction, case_id: str):
    if interaction.user.id not in ADMIN_IDS: return await interaction.response.send_message("⛔ Denied.", ephemeral=True)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
        await db.execute("DELETE FROM case_jackets WHERE case_id = ?", (case_id,))
        await db.commit()
    await interaction.response.send_message(f"🗑️ Deleted {case_id}.", ephemeral=True)

@client.tree.command(name="cid_help", description="System manual")
async def cid_help(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ CID/DTF System Manual", description="Authorized use only.", color=discord.Color.light_grey())
    embed.add_field(name="/file_case", value="Start a new investigation.", inline=False)
    embed.add_field(name="/edit_case", value="Update status, suspect, or narrative.", inline=False)
    embed.add_field(name="/case_directory", value="Scroll through all current cases.", inline=False)
    embed.add_field(name="/case_lookup", value="View details, evidence, and jackets.", inline=False)
    embed.add_field(name="/add_jacket", value="Link a Google Doc/PDF.", inline=False)
    embed.add_field(name="/add_evidence", value="Append a media link to narrative.", inline=False)
    embed.add_field(name="/import_case", value="Manually add a legacy case.", inline=False)
    embed.add_field(name="/delete_case", value="[ADMIN] Permanently wipe a case.", inline=False)
    await interaction.response.send_message(embed=embed)

client.run(TOKEN)
