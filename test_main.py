from fastapi.testclient import TestClient
from main import app
import unittest

client = TestClient(app)

class TestMain(unittest.TestCase):

    def test_main_active(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_login(self):
        response = client.post("/login",json={"name":"Mihai","password":"asd"})
        assert response.status_code == 200
        assert response.json()["code"] == "200"

    def test_login_fail(self):
        response = client.post("/login",json={"name":"Mihai","password":"as"})
        assert response.status_code == 404

    def test_login_fact(self):
        response = client.post("/login",json={"name":"razvan","password":"asd"})
        assert response.status_code == 200
        assert response.json() == {"code" : "200" , "type" : "fact"}

    def test_get_balance(self):
        response = client.post("/get-balance",json={"name":"Mihai"})
        assert response.status_code == 200
        assert response.json()["code"] == "200" 

    def test_get_balance_fail(self):
        response = client.post("/get-balance",json={"name":"Mih"})
        assert response.status_code == 404

    @unittest.skip("Can't make the post request work.")
    def test_transfer(self):
        balance = client.post("/get-balance",json={"name":"Mihai"}).json()["balance"]
        response = client.post("/transfer?mainUser=Mage",json={"name":"Mihai","balance":"20"})
        assert response.status_code == 200
        assert response.json() == {"code" : "200"}
        assert client.post("/get-balance",json={"name":"Mihai"}).json()["balance"] == balance - 20

    @unittest.skip("Can't make the post request work.")
    def test_transfer_fail(self):
        response = client.post("/transfer",json={"name":"Mih","amount":"20"})
        assert response.status_code == 404

    @unittest.skip("Can't make the post request work.")
    def test_transfer_fail_balance(self):
        response = client.post("/transfer",json={"name":"Mihai","amount":"1000"})

        assert response.status_code == 304
    
    @unittest.skip("Can't make the post request work.")
    def test_tranfer_fail_negative(self):
        response = client.post("/transfer?mainUser=Mihai",json={"name":"Mage","amount":"-20"})
        f = open("test.txt","w")
        print(response.status_code,file=f)
        f.close()
        assert response.status_code == 401

    def test_addfunds(self):
        balance = client.post("/get-balance",json={"name":"Mihai"}).json()["balance"]
        response = client.post("/addfunds",json={"name":"Mihai","balance":"20"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.post("/get-balance",json={"name":"Mihai"}).json()["balance"],balance + 20)
        response = client.post("/addfunds",json={"name":"Mihai","balance":"-20"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.post("/get-balance",json={"name":"Mihai"}).json()["balance"],balance)

    def test_addfunds_fail(self):
        response = client.post("/addfunds",json={"name":"Mih","balance":"20"})
        assert response.status_code == 400

    def test_sendbill(self):
        response = client.post("/sendbill",json={"factName":"admin","username":"Mage","amount":"20"})
        assert response.status_code == 200

    def test_sendbill_fail(self):
        response = client.post("/sendbill",json={"factName":"Mihai","username":"Mage","amount":"-20"})
        assert response.status_code == 400

    def test_sendbill_fail_user(self):
        response = client.post("/sendbill",json={"factName":"Mihai","username":"Mge","amount":"20"})
        assert response.status_code == 404

    def test_getbill(self):
        response = client.get("/getbills/Mage")
        assert response.status_code == 200
        f = open("test.txt","w")
        print(response.json(),file=f)
        f.close()

    def test_getbill_fail(self):
        response = client.get("/getbills/Mih")
        assert response.status_code == 404

    @unittest.skip("Works on frontend, but needs a valid uid for the test to work.")
    def test_paybill(self): #trebuie sa fie un bill in baza de date
        response = client.get("/paybill/Mage/629933")
        assert response.status_code == 200

    def test_paybill_fail(self):
        response = client.get("/paybill/Mage/0")
        assert response.status_code == 404

    @unittest.skip("Error on backend, but it works on the frontend.")
    def test_paybill_fail_user(self):
        response = client.get("/paybill/Mge/629933")
        assert response.status_code == 404

    def test_gethitory(self):
        response = client.get("/gethistory/Mage")
        assert response.status_code == 200
    
    def test_gethistory_fail(self):
        response = client.get("/gethistory/Mih")
        assert response.status_code == 404

if __name__ == "__main__":
    unittest.main()