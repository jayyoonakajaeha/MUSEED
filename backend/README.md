# MUSEED Backend API Specification

MUSEED 백엔드는 FastAPI로 구현된 RESTful API를 제공합니다.  
본 문서는 프론트엔드 연동 및 외부 시스템 통합을 위한 상세 API 명세서입니다.

- **Base URL:** (Local) `http://localhost:8000`
- **Auth:** JWT (Bearer Token)
- **Content-Type:** `application/json`

---

## 1. 인증 (Authentication)

### `POST /api/auth/signup`
신규 사용자 회원가입을 처리합니다.

**Request Body:**
```json
{
  "username": "jayyoon",
  "nickname": "Jay",
  "password": "securepassword123",
  "email": "jay@example.com"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "jayyoon",
  "nickname": "Jay",
  "email": "jay@example.com",
  "is_active": true
}
```

### `POST /api/auth/token`
사용자 로그인 및 JWT 액세스 토큰을 발급받습니다.

**Request Body (Form Data):**
*   `username`: 사용자 ID
*   `password`: 비밀번호

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 2. 사용자 관리 (User Management)

### `GET /api/users/{username}`
특정 사용자의 상세 프로필 정보를 조회합니다.

**Response:**
```json
{
  "id": 1,
  "username": "jayyoon",
  "nickname": "Jay",
  "email": "jay@example.com",
  "is_active": true,
  "profile_image_key": "Electronic",
  "is_followed_by_current_user": false,
  "followers_count": 12,
  "following_count": 5,
  "achievements": [
    {
      "id": "seed_planter",
      "name": "Seed Planter",
      "description": "Created your first playlist.",
      "icon": "🌱"
    }
  ],
  "playlists": [
    {
      "id": 10,
      "name": "Morning Vibes",
      "is_public": true,
      "created_at": "2024-12-14T09:00:00",
      "likes_count": 5,
      "liked_by_user": false
    }
  ],
  "liked_playlists": []
}
```

### `GET /api/users/feed`
팔로잉한 사용자들의 최근 활동(플레이리스트 생성, 좋아요 등) 피드를 조회합니다.

**Response:**
```json
[
  {
    "id": 101,
    "user": {
      "id": 2,
      "username": "music_fan",
      "nickname": "Fan",
      "profile_image_key": "Default"
    },
    "action_type": "create_playlist",
    "target_playlist": {
      "id": 15,
      "name": "Best of Jazz",
      "is_public": true
    },
    "created_at": "2024-12-14T10:30:00"
  }
]
```

### `GET /api/users/recommendations`
청취 기록 임베딩 유사도를 기반으로 취향이 비슷한 사용자를 추천합니다.

**Response:**
```json
[
  {
    "id": 5,
    "username": "jazz_lover",
    "nickname": "JazzCat",
    "profile_image_key": "Jazz",
    "similarity": 0.85
  }
]
```

### 기타 사용자 엔드포인트
*   `GET /api/users/search?q={query}`: 사용자 검색
*   `PUT /api/users/{username}`: 프로필 수정 (본인만 가능)
*   `GET /api/users/{username}/stats`: 사용자 Top Genre 통계
*   `GET /api/users/{username}/genre-stats`: 장르별 분포 데이터
*   `POST /api/users/{username}/follow`: 팔로우
*   `DELETE /api/users/{username}/follow`: 언팔로우
*   `GET /api/users/{username}/followers`: 팔로워 목록
*   `GET /api/users/{username}/following`: 팔로잉 목록

---

## 3. 플레이리스트 및 AI 생성 (Playlists & Generation)

### `POST /api/playlists` (AI Generation)
기존 트랙(Seed Track) ID를 기반으로 AI 플레이리스트 생성을 비동기 요청합니다.

**Request Body:**
```json
{
  "name": "My AI Playlist",
  "seed_track_id": 12345
}
```

**Response:**
```json
{
  "task_id": "c62a0c40-1234-5678-9abc-def012345678",
  "status": "processing",
  "message": "Playlist generation started in background."
}
```

### `GET /api/playlists/task/{task_id}`
AI 생성 작업의 상태를 확인합니다.

**Response (Processing):**
```json
{
  "task_id": "c62a0c40-...",
  "status": "PENDING",
  "result": null
}
```

**Response (Success):**
```json
{
  "task_id": "c62a0c40-...",
  "status": "SUCCESS",
  "result": { "playlist_id": 25 }
}
```

### `GET /api/playlists/{playlist_id}`
플레이리스트의 상세 정보와 포함된 트랙 목록을 조회합니다.

**Response:**
```json
{
  "id": 25,
  "name": "My AI Playlist",
  "is_public": true,
  "owner_id": 1,
  "created_at": "2024-12-14T12:00:00",
  "owner": {
    "id": 1,
    "username": "jayyoon",
    "nickname": "Jay"
  },
  "tracks": [
    {
      "id": 1,
      "position": 0,
      "track": {
        "track_id": 12345,
        "title": "Seed Song",
        "artist_name": "Artist A",
        "duration": 240,
        "genre_toplevel": "Electronic",
        "audio_url": "/api/tracks/12345/stream"
      }
    },
    {
      "id": 2,
      "position": 1,
      "track": {
        "track_id": 67890,
        "title": "Similar Track",
        "artist_name": "Artist B",
        "duration": 210,
        "genre_toplevel": "Electronic",
        "audio_url": "/api/tracks/67890/stream"
      }
    }
  ],
  "likes_count": 0,
  "liked_by_user": false
}
```

### `PUT /api/playlists/{playlist_id}/tracks/reorder`
플레이리스트 내 트랙 순서를 변경합니다.

**Request Body:**
```json
{
  "track_ids": [67890, 12345]
}
```

### 기타 플레이리스트 엔드포인트
*   `POST /api/playlists/upload`: 오디오 파일 업로드 기반 생성
*   `GET /api/playlists/discover`: 탐색용 공개 플레이리스트 목록
*   `GET /api/playlists/trending`: 트렌딩 플레이리스트
*   `GET /api/playlists/search?q={query}`: 플레이리스트 검색
*   `PUT /api/playlists/{playlist_id}`: 정보 수정
*   `DELETE /api/playlists/{playlist_id}`: 삭제
*   `POST /api/playlists/{playlist_id}/like`: 좋아요
*   `DELETE /api/playlists/{playlist_id}/like`: 좋아요 취소
*   `POST /api/playlists/{playlist_id}/tracks/{track_id}`: 트랙 추가
*   `DELETE /api/playlists/{playlist_id}/tracks/{track_id}`: 트랙 삭제

---

## 4. 트랙 및 오디오 (Tracks & Audio)

### `GET /api/tracks/search`
FMA 및 Jamendo 데이터베이스에서 트랙을 검색합니다.

**Query Params:** `q=piano`, `limit=5`

**Response:**
```json
[
  {
    "track_id": 555,
    "title": "Piano Sonata",
    "artist_name": "Classic Artist",
    "duration": 300,
    "genre_toplevel": "Classical",
    "audio_url": "/api/tracks/555/stream"
  }
  # ... more tracks
]
```

### `GET /api/tracks/{track_id}/stream`
해당 트랙의 오디오 파일을 스트리밍합니다.
*   **Header:** `Content-Type: audio/mpeg`

---

## 5. 청취 기록 (History)

### `POST /api/history/listen`
사용자가 곡을 재생했을 때 청취 기록을 저장합니다. (추천 시스템 및 통계용)

**Request Body:**
```json
{
  "track_id": 12345,
  "genre": "Electronic"
}
```

**Response:**
```json
{
  "id": 501,
  "user_id": 1,
  "track_id": 12345,
  "genre": "Electronic",
  "listened_at": "2024-12-14T12:05:00"
}
```

---

## 6. 시스템 상태 (System Status)

### `GET /api/status`
서버 헬스 체크용 엔드포인트입니다.
**Response:**
```json
{
  "status": "ok"
}
```

### `GET /api/stats`
서비스 전체 통계를 반환합니다 (총 유저 수, 트랙 수, 플레이리스트 수).
**Response:**
```json
{
  "tracks": 88224,
  "users": 150,
  "playlists": 450
}
```