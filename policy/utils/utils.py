from spil.models.spil import Spil

ckpt = {
    'SPIL': 'models/spil/checkpoints/epoch=5.ckpt'
}


def get_model(model_name: str):
    if model_name == 'SPIL':
        print(f"Loading {model_name} model ...")
        model = Spil.load_from_checkpoint(ckpt['SPIL'])
        model.freeze()
        print(f"{model_name} model successfully loaded!")
        return model

