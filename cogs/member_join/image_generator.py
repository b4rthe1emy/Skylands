import PIL.Image as Image
import PIL.ImageDraw
from rich import print
import nextcord
import dotenv

AVATAR_SIZE = 256
BORDER_SIZE = 20

WELCOME_IMAGE_FILE_PATH = dotenv.get_key(
    dotenv.find_dotenv(), "WELCOME_IMAGE_FILE_PATH"
)


async def generate_welcome_image(member: nextcord.Member):

    await member.avatar.save("image.png")
    image = Image.new(
        "RGBA",
        (BORDER_SIZE + AVATAR_SIZE + 600, BORDER_SIZE + AVATAR_SIZE + BORDER_SIZE),
        (0, 0, 0, 0),
    )
    pdp = Image.open("image.png")
    pdp = pdp.convert("RGBA")

    pdp = pdp.resize((AVATAR_SIZE, AVATAR_SIZE))

    # Circle crop
    # NOTE: If you use the circle crop, also switch the pdp to RGB mode.
    # height, width = pdp.size
    # lum_img = Image.new("L", [height, width], 0)
    # draw = PIL.ImageDraw.Draw(lum_img)
    # draw.pieslice([(0, 0), (height, width)], 0, 360, fill=255, outline="white")
    # img_arr = numpy.array(pdp)
    # lum_img_arr = numpy.array(lum_img)
    # final_img_arr = numpy.dstack((img_arr, lum_img_arr))
    # pdp = PIL.Image.fromarray(final_img_arr)

    image.alpha_composite(pdp, (BORDER_SIZE, BORDER_SIZE))

    draw = PIL.ImageDraw.Draw(image)
    draw.multiline_text(
        (BORDER_SIZE * 2 + AVATAR_SIZE, BORDER_SIZE + AVATAR_SIZE / 2 - 50),
        f"Bienvenue {member.global_name or member.name}\nsur Skylands !",
        (255, 255, 255),
        font_size=50,
        align="left",
    )

    image.save(WELCOME_IMAGE_FILE_PATH)
