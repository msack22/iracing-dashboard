import uvicorn
from infrastructure.config.settings import settings
from infrastructure.repositories.cars_repository import MockCarsRepository, IracingCarsRepository
from infrastructure.repositories.tracks_repository import MockTracksRepository, IracingTracksRepository
from infrastructure.repositories.member_repository import MockMemberRepository, IracingMemberRepository
from infrastructure.repositories.races_repository import MockRacesRepository, IracingRacesRepository
from infrastructure.auth.credentials_store import load_credentials
from presentation.app import create_app


def build_repos():
    if settings.use_mock:
        print("Mode: MOCK (datos de ejemplo)")
        return (
            MockCarsRepository(),
            MockTracksRepository(),
            MockMemberRepository(),
            MockRacesRepository(),
        )

    creds = load_credentials()
    if not creds:
        print("Mode: MOCK (sin credenciales configuradas — ingresalas desde la web)")
        return (
            MockCarsRepository(),
            MockTracksRepository(),
            MockMemberRepository(),
            MockRacesRepository(),
        )

    username, password = creds
    print(f"Mode: LIVE (conectado como {username})")
    try:
        from iracingdataapi.client import iRacingData
        client = iRacingData(username=username, password=password)
    except Exception as e:
        print(f"Error conectando a iRacing API: {e}. Usando datos mock.")
        return (
            MockCarsRepository(),
            MockTracksRepository(),
            MockMemberRepository(),
            MockRacesRepository(),
        )

    cid = settings.iracing_customer_id
    return (
        IracingCarsRepository(client),
        IracingTracksRepository(client),
        IracingMemberRepository(client, cid),
        IracingRacesRepository(client, cid),
    )


if __name__ == "__main__":
    cars_repo, tracks_repo, member_repo, races_repo = build_repos()
    app = create_app(cars_repo, tracks_repo, member_repo, races_repo)
    uvicorn.run(app, host="0.0.0.0", port=settings.port, reload=False)
