import uvicorn
from infrastructure.config.settings import settings
from infrastructure.repositories.cars_repository import MockCarsRepository, IracingCarsRepository
from infrastructure.repositories.tracks_repository import MockTracksRepository, IracingTracksRepository
from infrastructure.repositories.member_repository import MockMemberRepository, IracingMemberRepository
from infrastructure.repositories.races_repository import MockRacesRepository, IracingRacesRepository
from infrastructure.auth.credentials_store import load_credentials
from presentation.app import create_app


def _mock_repos():
    return (MockCarsRepository(), MockTracksRepository(), MockMemberRepository(), MockRacesRepository())


def build_repos():
    if settings.use_mock:
        print("Mode: MOCK (datos de ejemplo)")
        return _mock_repos()

    creds = load_credentials()
    if not creds:
        print("Mode: MOCK (sin credenciales — ingresalas desde la web)")
        return _mock_repos()

    username, password = creds
    try:
        from iracingdataapi.client import irDataClient
        client = irDataClient(username=username, password=password)
        # Verify auth works immediately with a lightweight call
        client.get_cars()
        print(f"Mode: LIVE (conectado como {username})")
    except Exception as e:
        print(f"Error conectando a iRacing API: {e}")
        print("Posibles causas: credenciales incorrectas, API de iRacing temporalmente no disponible.")
        print("Usando datos mock. Reiniciá el servidor para intentar reconectar.")
        return _mock_repos()

    cid = settings.iracing_customer_id
    return (
        IracingCarsRepository(client),
        IracingTracksRepository(client),
        IracingMemberRepository(client, cid),
        IracingRacesRepository(client, cid),
    )


if __name__ == "__main__":
    from infrastructure.storage.schedule_store import seed_catalog
    seed_catalog()
    cars_repo, tracks_repo, member_repo, races_repo = build_repos()
    app = create_app(cars_repo, tracks_repo, member_repo, races_repo)
    uvicorn.run(app, host="0.0.0.0", port=settings.port, reload=False)
