import io
import os
import warnings

from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
)

# observations = [":disappointed: :camera:",
#                 "Sorry I can only do so much with that prompt.",
#                 "I hope it comes back blank.",
#                 "It would literally be quicker to just click the link.",
#                 "50,000 times more intelligent than a human, and yet I am used to take pictures."]


def marvn_draw(prompt):
    marvn_prompt = f"depressing, hopeless, sad, dark, lonley {prompt}"
    return generate_image(marvn_prompt)


def generate_image(prompt):
    print(f"Got the prompt: {prompt}")
    # the object returned is a python generator
    answers = stability_api.generate(
        prompt=prompt,
        # seed=0,  # if provided, specifying a random seed makes results deterministic
        steps=50,  # defaults to 50 if not specified
    )

    # iterating over the generator produces the api response
    payload = {}
    try:
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")

                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.save(f"{os.environ.get('SCREENSHOT_DIR')}/genarated.png")
            payload = {"msg": prompt, "file": f"{os.environ.get('SCREENSHOT_DIR')}/genarated.png"}
    except Exception as e:
        payload = {"msg": f"The prompt: `{prompt}` activated the API's safety filters and could not be processed.",
                   "file": False}

    print(f"payload: {payload}")
    return payload


if __name__ == "__main__":
    print(marvn_draw("corgy on a motorcycle"))
