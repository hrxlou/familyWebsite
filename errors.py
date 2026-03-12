from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': '잘못된 요청입니다.', 'code': 400}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': '로그인이 필요합니다.', 'code': 401}), 401
        
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': '권한이 없습니다.', 'code': 403}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '요청한 리소스를 찾을 수 없습니다.', 'code': 404}), 404

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({'error': '리소스 충돌이 발생했습니다.', 'code': 409}), 409

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'error': '서버 내부 오류가 발생했습니다.', 'code': 500}), 500
